import { listInterventions } from "@/lib/db";
import { approveIntervention, rejectIntervention } from "./actions";

export const dynamic = "force-dynamic";

const ACTION_LABELS: Record<string, string> = {
  outreach_email: "Outreach email",
  advisor_meeting: "Advisor meeting",
  tutoring_referral: "Tutoring referral",
};

export default function QueuePage() {
  const pending = listInterventions("pending_approval");
  const decided = listInterventions()
    .filter((i) => i.status !== "pending_approval")
    .slice(0, 10);

  return (
    <main className="mx-auto max-w-3xl space-y-10 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-neutral-900">
          Approval queue
        </h1>
        <p className="mt-1 text-sm text-neutral-500">
          Nothing here was sent automatically - the agent can only queue a
          proposal. Approving or rejecting is the only thing that decides
          what actually happens.
        </p>
      </div>

      <section className="space-y-4">
        <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
          Pending ({pending.length})
        </h2>

        {pending.length === 0 && (
          <p className="rounded-lg border border-dashed border-neutral-300 p-6 text-sm text-neutral-500">
            No interventions are waiting on review.
          </p>
        )}

        {pending.map((intervention) => (
          <div
            key={intervention.id}
            className="space-y-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-neutral-900">
                Student #{intervention.student_id} &middot;{" "}
                {ACTION_LABELS[intervention.action_type] ?? intervention.action_type}
              </span>
              <span className="text-xs text-neutral-400">
                {intervention.created_at}
              </span>
            </div>

            <p className="text-sm text-neutral-600">{intervention.rationale}</p>

            <pre className="whitespace-pre-wrap rounded bg-neutral-50 p-3 text-sm text-neutral-700">
              {intervention.message_draft}
            </pre>

            <div className="flex gap-2">
              <form action={approveIntervention}>
                <input type="hidden" name="id" value={intervention.id} />
                <button
                  type="submit"
                  className="rounded bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700"
                >
                  Approve
                </button>
              </form>
              <form action={rejectIntervention}>
                <input type="hidden" name="id" value={intervention.id} />
                <button
                  type="submit"
                  className="rounded bg-neutral-200 px-3 py-1.5 text-sm font-medium text-neutral-700 hover:bg-neutral-300"
                >
                  Reject
                </button>
              </form>
            </div>
          </div>
        ))}
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
          Recent decisions
        </h2>

        {decided.length === 0 && (
          <p className="text-sm text-neutral-500">No decisions yet.</p>
        )}

        <ul className="divide-y divide-neutral-100 rounded-lg border border-neutral-200 bg-white">
          {decided.map((intervention) => (
            <li
              key={intervention.id}
              className="flex items-center justify-between px-4 py-2 text-sm"
            >
              <span>
                Student #{intervention.student_id} &middot;{" "}
                {ACTION_LABELS[intervention.action_type] ?? intervention.action_type}
              </span>
              <span
                className={
                  intervention.status === "executed"
                    ? "text-emerald-600"
                    : "text-neutral-400"
                }
              >
                {intervention.status}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
