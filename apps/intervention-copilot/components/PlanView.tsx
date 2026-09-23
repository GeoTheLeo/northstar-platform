import type { PlanStep } from "@/lib/events";

export function PlanView({ steps }: { steps: PlanStep[] }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-neutral-400">
        Plan
      </h3>
      <ol className="space-y-2">
        {steps.map((step, i) => (
          <li key={i} className="flex gap-3 text-sm">
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-neutral-900 text-xs font-medium text-white">
              {i + 1}
            </span>
            <div>
              <p className="text-neutral-800">
                {step.step}
                {step.tool_hint && (
                  <code className="ml-2 rounded bg-neutral-100 px-1.5 py-0.5 text-xs text-neutral-500">
                    {step.tool_hint}
                  </code>
                )}
              </p>
              <p className="text-xs text-neutral-400">{step.rationale}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
