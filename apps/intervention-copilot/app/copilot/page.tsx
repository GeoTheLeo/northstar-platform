import { CopilotConsole } from "@/components/CopilotConsole";

export default function CopilotPage() {
  return (
    <main className="mx-auto max-w-3xl space-y-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-neutral-900">
          Intervention Copilot
        </h1>
        <p className="mt-1 text-sm text-neutral-500">
          The agent plans first, then investigates using real risk/segment
          data. It can queue an intervention for review, but it can never
          send or execute one - that always requires a human in the{" "}
          <a href="/queue" className="underline">
            approval queue
          </a>
          .
        </p>
      </div>

      <CopilotConsole />
    </main>
  );
}
