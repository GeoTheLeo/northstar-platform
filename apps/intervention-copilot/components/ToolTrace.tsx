export interface TraceEntry {
  id: string;
  name: string;
  input: unknown;
  result?: unknown;
  isError?: boolean;
}

export function ToolTrace({ entries }: { entries: TraceEntry[] }) {
  if (entries.length === 0) return null;

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-neutral-400">
        Tool activity
      </h3>
      <ul className="space-y-3">
        {entries.map((entry) => (
          <li key={entry.id} className="text-sm">
            <div className="flex items-center gap-2">
              <span
                className={
                  entry.result === undefined
                    ? "h-2 w-2 animate-pulse rounded-full bg-amber-400"
                    : entry.isError
                      ? "h-2 w-2 rounded-full bg-red-500"
                      : "h-2 w-2 rounded-full bg-emerald-500"
                }
              />
              <code className="font-medium text-neutral-800">{entry.name}</code>
            </div>
            <pre className="mt-1 ml-4 overflow-x-auto rounded bg-neutral-50 p-2 text-xs text-neutral-500">
              {JSON.stringify(entry.input)}
            </pre>
            {entry.result !== undefined && (
              <pre
                className={
                  entry.isError
                    ? "mt-1 ml-4 overflow-x-auto rounded bg-red-50 p-2 text-xs text-red-700"
                    : "mt-1 ml-4 overflow-x-auto rounded bg-emerald-50 p-2 text-xs text-emerald-800"
                }
              >
                {typeof entry.result === "string"
                  ? entry.result
                  : JSON.stringify(entry.result)}
              </pre>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
