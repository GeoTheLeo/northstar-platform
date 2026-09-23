import { runAgent } from "@/lib/agent";
import type { AgentEvent } from "@/lib/events";

// better-sqlite3 and the Anthropic Node SDK need the Node runtime, not Edge.
export const runtime = "nodejs";

export async function POST(req: Request): Promise<Response> {
  let message: unknown;

  try {
    const body = await req.json();
    message = body?.message;
  } catch {
    return new Response("invalid JSON body", { status: 400 });
  }

  if (typeof message !== "string" || !message.trim()) {
    return new Response("`message` is required", { status: 400 });
  }

  const encoder = new TextEncoder();

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const send = (event: AgentEvent) => {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`));
      };

      try {
        await runAgent(message as string, send);
      } catch (err) {
        send({
          type: "error",
          message: err instanceof Error ? err.message : String(err),
        });
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
