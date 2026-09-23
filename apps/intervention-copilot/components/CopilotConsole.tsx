"use client";

import { useState } from "react";
import type { AgentEvent, PlanStep } from "@/lib/events";
import { PlanView } from "./PlanView";
import { ToolTrace, type TraceEntry } from "./ToolTrace";

const EXAMPLE_PROMPT =
  "Find students at risk and propose an outreach intervention for the most urgent one.";

type Status = "idle" | "running" | "done" | "error";

export function CopilotConsole() {
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [plan, setPlan] = useState<PlanStep[] | null>(null);
  const [trace, setTrace] = useState<TraceEntry[]>([]);
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!message.trim() || status === "running") return;

    setStatus("running");
    setPlan(null);
    setTrace([]);
    setText("");
    setError(null);

    try {
      const res = await fetch("/api/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!res.ok || !res.body) {
        throw new Error(`Request failed (${res.status})`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() ?? "";

        for (const chunk of chunks) {
          const line = chunk.trim();
          if (!line.startsWith("data:")) continue;

          const event = JSON.parse(line.slice("data:".length).trim()) as AgentEvent;
          applyEvent(event);
        }
      }

      setStatus((s) => (s === "error" ? s : "done"));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setStatus("error");
    }
  }

  function applyEvent(event: AgentEvent) {
    switch (event.type) {
      case "plan":
        setPlan(event.steps);
        break;
      case "text":
        setText((t) => t + event.text);
        break;
      case "tool_call":
        setTrace((prev) => [
          ...prev,
          { id: event.id, name: event.name, input: event.input },
        ]);
        break;
      case "tool_result":
        setTrace((prev) =>
          prev.map((entry) =>
            entry.id === event.id
              ? { ...entry, result: event.result, isError: event.is_error }
              : entry,
          ),
        );
        break;
      case "error":
        setError(event.message);
        setStatus("error");
        break;
      case "done":
        setStatus("done");
        break;
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-2">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={EXAMPLE_PROMPT}
          rows={3}
          disabled={status === "running"}
          className="w-full rounded-lg border border-neutral-300 p-3 text-sm focus:border-neutral-500 focus:outline-none disabled:bg-neutral-100"
        />
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={status === "running" || !message.trim()}
            className="rounded bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {status === "running" ? "Working..." : "Send"}
          </button>
          <button
            type="button"
            onClick={() => setMessage(EXAMPLE_PROMPT)}
            className="text-xs text-neutral-400 hover:text-neutral-600"
          >
            Use example prompt
          </button>
        </div>
      </form>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {plan && <PlanView steps={plan} />}

      <ToolTrace entries={trace} />

      {text && (
        <div className="rounded-lg border border-neutral-200 bg-white p-4 text-sm whitespace-pre-wrap text-neutral-800">
          {text}
        </div>
      )}
    </div>
  );
}
