import { randomUUID } from "crypto";
import { betaZodTool } from "@anthropic-ai/sdk/helpers/beta/zod";
import { z } from "zod";
import { fetchAtRiskStudents, fetchStudentDetail } from "./copilotApi";
import {
  createIntervention,
  getInterventionPolicyCooldownDays,
  hasRecentIntervention,
} from "./db";
import type { EmitEvent } from "./events";

const ACTION_TYPES = [
  "outreach_email",
  "advisor_meeting",
  "tutoring_referral",
] as const;

export const TOOL_CATALOG = [
  {
    name: "list_at_risk_students",
    description:
      "List students the early-warning model currently flags as at-risk, sorted by risk confidence descending.",
  },
  {
    name: "get_student_detail",
    description:
      "Get a single student's raw scores, risk prediction, and learner segment (cluster).",
  },
  {
    name: "check_intervention_policy",
    description:
      `Check whether a new intervention is allowed for a student (at most one active proposal per student every ${getInterventionPolicyCooldownDays()} days).`,
  },
  {
    name: "propose_intervention",
    description:
      "Queue a proposed intervention for a student. NEVER executes anything - only creates a pending record a human must approve.",
  },
] as const;

// Wraps a tool's run() so every invocation is traced to the client as a
// tool_call/tool_result pair, regardless of how the tool runner streams it.
function traced<Input, Output>(
  onEvent: EmitEvent,
  name: string,
  run: (input: Input) => Promise<Output>,
): (input: Input) => Promise<Output> {
  return async (input: Input) => {
    const id = randomUUID();
    onEvent({ type: "tool_call", id, name, input });

    try {
      const result = await run(input);
      onEvent({ type: "tool_result", id, name, result });
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      onEvent({ type: "tool_result", id, name, result: message, is_error: true });
      throw err;
    }
  };
}

export function createTools(onEvent: EmitEvent) {
  const listAtRiskStudents = betaZodTool({
    name: "list_at_risk_students",
    description:
      "List students the early-warning model currently flags as at-risk, sorted by risk confidence descending. Call this first to see who might need an intervention.",
    inputSchema: z.object({
      min_confidence: z
        .number()
        .min(0)
        .max(1)
        .optional()
        .describe(
          "Only return students with at least this model confidence (0-1). Omit to return all at-risk students.",
        ),
    }),
    run: traced(onEvent, "list_at_risk_students", async ({ min_confidence }) => {
      const students = await fetchAtRiskStudents(min_confidence ?? 0);
      return JSON.stringify(students);
    }),
  });

  const getStudentDetail = betaZodTool({
    name: "get_student_detail",
    description:
      "Get a single student's raw scores, early-warning risk prediction, and learner segment (cluster). Call this before proposing an intervention so the rationale can cite the student's actual numbers.",
    inputSchema: z.object({
      student_id: z.number().int().describe("The student's numeric ID."),
    }),
    run: traced(onEvent, "get_student_detail", async ({ student_id }) => {
      const detail = await fetchStudentDetail(student_id);
      return JSON.stringify(detail);
    }),
  });

  const checkInterventionPolicy = betaZodTool({
    name: "check_intervention_policy",
    description:
      `Check whether a new intervention is allowed for a student right now. Policy: at most one active (pending or executed) intervention per student every ${getInterventionPolicyCooldownDays()} days. Call this before propose_intervention to avoid proposing an action that will be rejected.`,
    inputSchema: z.object({
      student_id: z.number().int(),
    }),
    run: traced(onEvent, "check_intervention_policy", async ({ student_id }) => {
      const blocked = hasRecentIntervention(student_id);
      return JSON.stringify({
        allowed: !blocked,
        reason: blocked
          ? `Student ${student_id} already has a pending or executed intervention within the last ${getInterventionPolicyCooldownDays()} days.`
          : null,
      });
    }),
  });

  const proposeIntervention = betaZodTool({
    name: "propose_intervention",
    description:
      "Queue a proposed intervention (e.g. outreach email, advisor meeting, tutoring referral) for a student. This NEVER executes anything directly - it only creates a pending record that a human must review and approve in the approval queue UI before anything happens. Always call check_intervention_policy first.",
    inputSchema: z.object({
      student_id: z.number().int(),
      action_type: z.enum(ACTION_TYPES),
      rationale: z
        .string()
        .describe(
          "Why this student and this action, citing their actual scores/segment.",
        ),
      message_draft: z
        .string()
        .describe(
          "Draft text of the outreach message or meeting agenda a human would use if approved.",
        ),
    }),
    run: traced(onEvent, "propose_intervention", async (input) => {
      if (hasRecentIntervention(input.student_id)) {
        return JSON.stringify({
          queued: false,
          reason: `Blocked by policy: student ${input.student_id} already has a pending or executed intervention within the last ${getInterventionPolicyCooldownDays()} days.`,
        });
      }

      const intervention = createIntervention(input);
      return JSON.stringify({
        queued: true,
        intervention,
        note: "Queued for human review only. No message has been sent and no action has been taken yet.",
      });
    }),
  });

  // eager_input_streaming: stream tool inputs as they're generated rather
  // than buffering each parameter until it's complete (see the Claude API
  // streaming guide's tool-use section).
  return [
    listAtRiskStudents,
    getStudentDetail,
    checkInterventionPolicy,
    proposeIntervention,
  ].map((tool) => ({ ...tool, eager_input_streaming: true }));
}
