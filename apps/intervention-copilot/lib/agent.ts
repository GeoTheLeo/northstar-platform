import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { z } from "zod";
import { createTools, TOOL_CATALOG } from "./tools";
import type { AgentEvent, EmitEvent, PlanStep } from "./events";

const MODEL = "claude-opus-5";

const PlanSchema = z.object({
  steps: z
    .array(
      z.object({
        step: z.string().describe("A short imperative description of this step."),
        tool_hint: z
          .string()
          .nullable()
          .describe(
            "Name of the tool this step will most likely use, or null if it's pure reasoning/summary.",
          ),
        rationale: z.string().describe("Why this step is needed."),
      }),
    )
    .min(1)
    .max(6),
});

const PLAN_SYSTEM_PROMPT = `You are the planning module for NorthStar's Agentic Intervention Copilot, which helps staff identify at-risk students and propose interventions.

Available tools:
${TOOL_CATALOG.map((t) => `- ${t.name}: ${t.description}`).join("\n")}

Given the user's request, produce a short ordered plan (1-6 steps) of what you will do, before doing any of it. Each step should name the tool it will likely use (or null for a pure reasoning/summary step). Keep steps concise.`;

function buildExecuteSystemPrompt(steps: PlanStep[]): string {
  const planText = steps
    .map(
      (s, i) =>
        `${i + 1}. ${s.step}${s.tool_hint ? ` [${s.tool_hint}]` : ""} - ${s.rationale}`,
    )
    .join("\n");

  return `You are NorthStar's Agentic Intervention Copilot. You already produced this plan for the user's request - follow it, adapting only if a tool result requires it:

${planText}

Rules:
- Never state a student's scores, risk, or segment without first calling get_student_detail (or list_at_risk_students) to look them up.
- Always call check_intervention_policy before propose_intervention for a given student.
- propose_intervention only queues an action for a human to review in the approval queue - it never sends anything or takes real effect. Say this explicitly in your final summary so the user knows nothing has actually happened yet.
- Be concise. End with a short summary of what you found and what (if anything) is now pending human approval.`;
}

async function planPhase(
  client: Anthropic,
  userMessage: string,
): Promise<PlanStep[]> {
  const response = await client.messages.parse({
    model: MODEL,
    max_tokens: 2000,
    system: PLAN_SYSTEM_PROMPT,
    output_config: { format: zodOutputFormat(PlanSchema) },
    messages: [{ role: "user", content: userMessage }],
  });

  if (!response.parsed_output) {
    throw new Error("planning phase did not return a parseable plan");
  }

  return response.parsed_output.steps;
}

export async function runAgent(
  userMessage: string,
  onEvent: EmitEvent,
): Promise<void> {
  const client = new Anthropic();

  try {
    const steps = await planPhase(client, userMessage);
    onEvent({ type: "plan", steps });

    const tools = createTools(onEvent);
    const system = buildExecuteSystemPrompt(steps);

    const runner = client.beta.messages.toolRunner({
      model: MODEL,
      max_tokens: 8000,
      system,
      tools,
      stream: true,
      messages: [{ role: "user", content: userMessage }],
    });

    for await (const messageStream of runner) {
      for await (const event of messageStream) {
        if (
          event.type === "content_block_delta" &&
          event.delta.type === "text_delta"
        ) {
          onEvent({ type: "text", text: event.delta.text });
        }
      }

      const message = await messageStream.finalMessage();

      if (message.stop_reason === "refusal") {
        onEvent({ type: "error", message: "The model declined to continue." });
        break;
      }

      if (message.stop_reason === "pause_turn") {
        runner.pushMessages({ role: "assistant", content: message.content });
      }
    }

    onEvent({ type: "done" });
  } catch (err) {
    onEvent({ type: "error", message: describeError(err) });
  }
}

function describeError(err: unknown): string {
  if (err instanceof Anthropic.RateLimitError) {
    return "Rate limited by the Claude API - please try again shortly.";
  }
  if (err instanceof Anthropic.AuthenticationError) {
    return "Claude API authentication failed - check ANTHROPIC_API_KEY.";
  }
  if (err instanceof Anthropic.APIError) {
    return `Claude API error (${err.status ?? "unknown status"}): ${err.message}`;
  }
  if (err instanceof Anthropic.APIConnectionError) {
    return "Could not reach the Claude API - check network connectivity.";
  }
  if (err instanceof Error) {
    return err.message;
  }
  return String(err);
}

export type { AgentEvent };
