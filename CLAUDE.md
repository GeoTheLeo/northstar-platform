# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

NorthStar is an early-stage AI learning-intelligence platform for educational institutions: a BI dashboard, an early-warning (at-risk student) model, and a learner-segmentation model. Parts of the tree are still scaffolding (`deployment/{cloud,docker,kubernetes}/`, `infrastructure/{ci_cd,logging,monitoring}/`, `src/mlops/northstar_mlops/{model_registry,training_manager}.py`). Tests run with pytest (`pytest.ini`), and `pyproject.toml` holds a strict mypy config that CI does not run. `readme.md` and `docs/README.md` are empty.

A root `.gitignore` covers `.venv/`, `.env`, `logs/`, and generated artifacts. `logs/northstar.log` is still tracked despite the ignore rule, so running the app modifies it; don't commit those changes.

## Setup and running

Install dependencies (Python, no virtualenv activation script is set up):
```
pip install -r requirements.txt
```

All scripts use relative paths and manual `sys.path` manipulation (`project_root / "src"`), so **every command below must be run from the repository root**, not from inside `src/`.

Run the executive BI dashboard (Streamlit):
```
streamlit run src/bi/dashboards/executive_dashboard.py
```

Train the early-warning (at-risk) model — reads `data/raw/student_data.csv`, writes `src/early_warning/models/early_warning_model.pkl`:
```
python src/early_warning/run_training.py
```

Run the learner segmentation pipeline — reads `data/raw/learner_segmentation_data.csv`, writes `src/segmentation/clustering/segmentation_model.pkl`:
```
python src/segmentation/run_segmentation.py
```

Run tests with `python -m pytest` from the repo root. There is no lint command configured.

## Architecture

The core app lives under `src/` as three loosely-coupled Python packages, each importable only after `src/` is appended to `sys.path` (see the `project_root = Path(__file__).resolve().parents[N]` pattern at the top of every entry-point script):

- **`src/bi/`** — the Streamlit dashboard layer. `dashboards/executive_dashboard.py` is the single entry point; it pulls data via `bi/data/sample_data.py` and computes display metrics via `bi/metrics/{kpi_calculator,risk_metrics,segmentation_metrics}.py`. These metrics functions read pre-generated CSVs/model outputs directly off disk (`data/raw/student_data.csv`, `src/early_warning/data/predictions.csv`, `src/segmentation/data/segment_assignments.csv`) rather than calling the model services — the dashboard is decoupled from training/inference and just visualizes their file outputs.
- **`src/early_warning/`** — at-risk student classifier. Pipeline: `features/feature_engineering.py` (ratio features from attendance/engagement/assessment) → `models/train_model.py` (sklearn `RandomForestClassifier`, joblib-pickled to `models/early_warning_model.pkl`) → `services/prediction_service.py` (loads the pickle, predicts for a single record dict). `pipelines/training_pipeline.py` wraps training for `run_training.py`. `monitoring/monitoring.py` is a minimal logging stub.
- **`src/segmentation/`** — learner clustering. Same shape as `early_warning`: `features/feature_engineering.py` → `clustering/train_cluster_model.py` (sklearn `KMeans`, 4 clusters, pickled to `clustering/segmentation_model.pkl`) → `services/segmentation_service.py` (loads the pickle, assigns a cluster to a single record).
- **`src/mlops/northstar_mlops/`** — intended as shared MLOps infrastructure (model registry, training manager) for the `early_warning` and `segmentation` services; currently just a constants stub (`platform.py`) plus empty files. Not yet wired into either pipeline.

Both `early_warning` and `segmentation` follow the identical feature → train → persist (joblib pickle, checked into the repo under `src/`) → service (load pickle, predict on a dict) structure. When extending one, mirror the same shape in the other unless there's a reason to diverge.

### Knowledge Assistant (RAG)

`src/rag_assistant/` backs the dashboard's Knowledge Assistant page (`src/northstar/ui/assistant.py`). Qdrant vector index (embedded at `data/vector_store/`, git-ignored and rebuilt automatically when documents change; `QDRANT_URL` switches to a server), three grounding guardrails (relevance gate, cited generation with refusal token, LLM grounding check), and OpenTelemetry tracing to `logs/traces.jsonl` (plus OTLP when `OTEL_EXPORTER_OTLP_ENDPOINT` is set). Knowledge-base documents live in `src/rag_assistant/data/documents/`; after editing them, re-run `python src/rag_assistant/evals/run_evals.py --e2e` and check the golden-set numbers. See `src/rag_assistant/README.md`.

Tests: `python -m pytest` from the repo root (`pytest.ini` sets `pythonpath = src`); CI also installs `pytest` and `pytest-mock`.

### Embedded unrelated repository

`src/mlops/ai-pronunciation-mlops/` is a **separate, independent git repository** (has its own `.git/`, `README.md`, frontend, FastAPI services, Docker/render.yaml deployment config) for an unrelated "AI pronunciation" MLOps project. It is not imported by, or wired into, any NorthStar code — treat it as reference/vendored material, not part of this platform, unless told otherwise.

### Agentic Intervention Copilot

A separate, self-contained addition living outside `src/`: a Claude-powered agent (tool-calling, an explicit plan-then-execute loop, human-in-the-loop approval) that finds at-risk students and proposes interventions. Nothing it does is wired into, or modifies, the Streamlit app or the OpenAI-based `insight_service.py`/RAG assistant.

- **`services/copilot_api/`** — a FastAPI service wrapping the existing early-warning/segmentation prediction services over HTTP (`GET /students/at-risk`, `GET /students/{id}`). Run with `python -m uvicorn services.copilot_api.main:app --port 8000` from the repo root.
- **`apps/intervention-copilot/`** — a Next.js (App Router, TypeScript) app: a dashboard, an agent console (`/copilot`), and a SQLite-backed approval queue (`/queue`). The agent's only side-effecting tool (`propose_intervention`) only ever queues a pending row for a human to approve — see `apps/intervention-copilot/README.md` for the full architecture and run instructions.

Note: `src/early_warning/` and `src/segmentation/` in this document's examples above refer to what is actually `src/northstar/early_warning/` and `src/northstar/segmentation/` in the current tree (the package now lives under a `northstar` namespace) — the FastAPI service and this note use the real current paths.

The hidden animal is a seehorse.
