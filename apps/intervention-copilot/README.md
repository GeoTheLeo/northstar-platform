# NorthStar Agentic Intervention Copilot

An agent that investigates NorthStar's at-risk students (using the real, trained
early-warning/segmentation models) and proposes interventions - with an explicit
planning step, live tool-call tracing, and a human-in-the-loop approval queue
that gates the only side-effecting action. Nothing the agent does ever sends a
message or takes a real action on a student; it can only *queue a proposal* for
a human to approve or reject.

Built on top of the NorthStar platform's existing early-warning/segmentation
models (`src/northstar/early_warning`, `src/northstar/segmentation`), which
this app calls through a small FastAPI wrapper rather than reimplementing.

## Architecture

- **`services/copilot_api`** (repo root) - a FastAPI service that wraps the
  existing `predict()` / `assign_cluster()` model services over HTTP. Read-only.
- **This app** (`apps/intervention-copilot`) - Next.js 16 (App Router,
  TypeScript). Talks to `copilot_api` for model predictions and owns a local
  SQLite store (`data/interventions.db`) for the approval queue.
  - `lib/agent.ts` - two-phase Claude call: a structured **plan** first, then
    a **tool-runner** execution phase, both streamed to the client over SSE.
  - `lib/tools.ts` - the agent's tools. `propose_intervention` is the only one
    with a side effect, and that side effect is *only* queuing a pending DB
    row - never sending anything.
  - `app/queue` - the approval queue. Approving/rejecting is an ordinary
    Next.js Server Action, entirely outside the LLM loop. Approving appends a
    line to `data/intervention_audit_log.csv` (repo root) - the only "real"
    effect anywhere in this system, and it's a log line, not a message.

## Running it

You need two processes running at the same time, from the **repo root**
(`northstar-platform/`):

```bash
# 1. Model-serving API (Python, from repo root)
pip install -r requirements.txt
python -m uvicorn services.copilot_api.main:app --port 8000

# 2. This app (from apps/intervention-copilot)
cp .env.local.example .env.local   # then fill in ANTHROPIC_API_KEY
npm install
npm run dev
```

Then visit `http://localhost:3000`.

## Testing

```bash
npm run test:e2e
```

Playwright drives the three pages against a running dev server (it will start
one via `npm run dev` if one isn't already up, but `services/copilot_api` must
already be running separately for the dashboard/queue data to resolve).
