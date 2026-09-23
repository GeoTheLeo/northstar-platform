export interface PlanStep {
  step: string;
  tool_hint: string | null;
  rationale: string;
}

export type AgentEvent =
  | { type: "plan"; steps: PlanStep[] }
  | { type: "text"; text: string }
  | { type: "tool_call"; id: string; name: string; input: unknown }
  | { type: "tool_result"; id: string; name: string; result: unknown; is_error?: boolean }
  | { type: "done" }
  | { type: "error"; message: string };

export type EmitEvent = (event: AgentEvent) => void;
