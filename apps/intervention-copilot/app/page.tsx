import Link from "next/link";
import { fetchAtRiskStudents } from "@/lib/copilotApi";
import { listInterventions } from "@/lib/db";

export const dynamic = "force-dynamic";

function daysAgo(iso: string): number {
  return (Date.now() - new Date(iso + "Z").getTime()) / (1000 * 60 * 60 * 24);
}

async function getKpis() {
  const [atRisk, interventions] = await Promise.all([
    fetchAtRiskStudents().catch(() => []),
    Promise.resolve(listInterventions()),
  ]);

  const pending = interventions.filter((i) => i.status === "pending_approval");
  const executedThisWeek = interventions.filter(
    (i) => i.status === "executed" && i.decided_at && daysAgo(i.decided_at) <= 7,
  );

  return {
    atRiskCount: atRisk.length,
    pendingCount: pending.length,
    executedThisWeekCount: executedThisWeek.length,
  };
}

export default async function DashboardPage() {
  const { atRiskCount, pendingCount, executedThisWeekCount } = await getKpis();

  return (
    <main className="mx-auto max-w-4xl space-y-10 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-neutral-900">
          NorthStar Intervention Copilot
        </h1>
        <p className="mt-1 text-sm text-neutral-500">
          An agent that investigates at-risk students and proposes
          interventions - a human always approves before anything happens.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <KpiCard label="Students at risk" value={atRiskCount} />
        <KpiCard label="Pending approvals" value={pendingCount} accent />
        <KpiCard label="Executed this week" value={executedThisWeekCount} />
      </div>

      <div className="flex gap-3">
        <Link
          href="/copilot"
          className="rounded bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-700"
        >
          Open the copilot console
        </Link>
        <Link
          href="/queue"
          className="rounded bg-neutral-100 px-4 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-200"
        >
          Review approval queue
        </Link>
      </div>
    </main>
  );
}

function KpiCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: boolean;
}) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <p className="text-sm text-neutral-500">{label}</p>
      <p
        className={
          accent
            ? "mt-2 text-3xl font-semibold text-amber-600"
            : "mt-2 text-3xl font-semibold text-neutral-900"
        }
      >
        {value}
      </p>
    </div>
  );
}
