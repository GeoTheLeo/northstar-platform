# Phase 1: Container images, before and after

**Date:** 2026-10-22 · **Branch:** `k8s-platform`

NorthStar used to ship as one image (`Dockerfile` at the repo root) holding everything:
Streamlit, the RAG stack with GPU-build torch, and the inference API's dependencies. Phase 1
splits it into two purpose-built images:

| Image | Dockerfile | Contains |
|---|---|---|
| `northstar-api` | `deployment/docker/api.Dockerfile` | FastAPI inference API (`services/copilot_api`): sklearn models only, no torch, Streamlit or RAG |
| `northstar-dashboard` | `deployment/docker/dashboard.Dockerfile` | Streamlit dashboard, including the in-process Knowledge Assistant (RAG) |

The root `Dockerfile` is unchanged and is the baseline below.

## Results

| | Baseline | API image | Dashboard image |
|---|---|---|---|
| Size on disk | 9.21 GB | **696 MB** | **2.99 GB** |
| Download size (compressed) | 3.11 GB | **158 MB** | **733 MB** |
| GPU (nvidia-*) packages | 15 | 0 | 0 |
| Runs as | root | non-root (uid 10001) | non-root (uid 10001) |
| Built-in health check | no | yes | yes |
| Ships the unrelated `ai-pronunciation-mlops` repo (incl. its `.git`) | yes | no | no |
| Python library vulnerabilities (Trivy) | 83 (6 critical, 50 high) | **0** | 28 (3 critical), all pillow, [accepted with justification](#pillow-risk-acceptance) |
| OS package vulnerabilities (Debian base) | 164, 0 fixable | 164, 0 fixable | 164, 0 fixable |
| Healthy after start | 3.6 s / 2.9 s | 5.7 s / 3.2 s | 3.3 s / 4.1 s |
| First full page render | 34.2 s / 37.2 s | n/a | **17.0 s / 17.2 s** |
| First Knowledge Assistant retrieval | 10.1 s / 10.5 s | n/a | **2.1 s / 2.0 s** |

Pairs of numbers are two separate cold starts (`docker run` on a fresh container each time).

### What made the difference

- **CPU-only torch.** On Linux, `pip install torch` pulls the CUDA build plus about 3 GB of
  `nvidia-*` wheels that a CPU-only pod can never use. The dashboard installs torch from
  PyTorch's CPU index first.
- **Separate dependency sets.** The API needs pandas, scikit-learn and FastAPI
  (`requirements/api.txt`), not the 2+ GB RAG stack.
- **RAG models baked in.** The embedding model (`all-MiniLM-L6-v2`) and reranker
  (`cross-encoder/ms-marco-MiniLM-L6-v2`) are downloaded at build time and the image runs with
  `HF_HUB_OFFLINE=1`. The baseline downloads them from Hugging Face on first use, which is most of
  its 10 s first retrieval. A new pod now does its first retrieval without internet access.
- **Multi-stage builds.** Dependencies are installed in a builder stage. The runtime stage copies
  only the virtualenv and the code it needs, and removes `pip`, `setuptools` and `wheel` (never
  used at runtime, and the source of most of the API image's remaining findings).
- **Tighter `.dockerignore`.** Excludes nested `.git` folders, `.env` files, `apps/`,
  `deployment/`, `infrastructure/` and the embedded pronunciation repo.
- **Dependency bumps** (`requirements.txt`, patch/minor only): anyio 4.14.2, certifi
  2026.10.19, GitPython 3.1.62, pillow 12.3.0, starlette 1.3.1, urllib3 2.8.0. These cleared
  the critical findings in anyio, certifi and GitPython, and 13 of pillow's 41.

### What did not improve, and why

- **Clean build time** varies with network speed, because it's mostly package downloads:
  baseline 12.7 min; API 75–112 s; dashboard 7.5–10.8 min across runs. Both the old and new
  Dockerfiles install dependencies before copying code, so a code-only change rebuilds in
  seconds either way (dashboard: 23 s).
- **Time to healthy** is about 3–5 s for every image. The Streamlit health endpoint answers
  before any real work happens. The difference shows up in the first render and first
  retrieval.
- **OS vulnerabilities** are identical in all three images: the same 164 findings in the
  `python:3.11-slim` (Debian 13) base, with no fixed versions published yet. Reducing them
  means a smaller base image (for example distroless). Possible follow-up.

## Bug found by running as non-root

The non-root dashboard crashed on its first render with
`PermissionError: .../segmentation/clustering/segmentation_model.pkl`.
`SegmentationService.segment()` called `train_segmentation_model()`, which **retrained KMeans and
overwrote the saved model file on every dashboard load**. That is the same artifact the inference
API serves. The baseline only hid it by running as root. On Kubernetes with several replicas,
every page view would rewrite a model that other pods are reading.

Fix: `train_segmentation_model(df, persist=False)` for runtime callers. The dashboard still fits
clusters on the fly, so its output is unchanged, but only the training script
(`run_segmentation.py`) writes the artifact. Covered by
`tests/services/test_segmentation_service.py::test_segment_does_not_overwrite_saved_model`.

Open design question, not changed here: should the dashboard use the registered model instead of
fitting its own each time?

## Pillow risk acceptance

All 28 remaining dashboard findings are in pillow and are fixed only in pillow 13.0.0. Streamlit
1.58.0, the version Streamlit Community Cloud runs, requires `pillow<13`, and 12.3.0 is the
newest allowed version (already pinned). Every finding is triggered by decoding a crafted image.
NorthStar never decodes user-supplied images: there is no `file_uploader`, `camera_input`,
`Image.open` or `st.image` in `src/northstar` or `src/rag_assistant`. The API image doesn't
contain pillow at all.

The acceptance is recorded per CVE in `.trivyignore.yaml`, with an expiry date (2027-01-31). After
that date the scan fails again until someone reviews it. Re-check whenever Streamlit is upgraded.

## How these numbers were measured

- **Machine:** Windows 11, Docker Desktop 29.7.2 (WSL 2), 16 logical CPUs, 23 GB RAM. Runs were
  sequential, with nothing else building or scanning.
- **Size:** `docker image ls` (on disk) and `docker image inspect --format '{{.Size}}'`
  (compressed).
- **Build time:** `docker build --no-cache`, wall clock.
- **Healthy:** time from `docker run` until `/health` (API) or `/_stcore/health` (dashboard)
  answers.
- **Render and retrieval:** a script run inside the container that renders `src/northstar/app.py`
  with Streamlit's `AppTest` (home page only) and then calls
  `rag_assistant.retrieval.retriever.retrieve_documents()` once.
- **Vulnerabilities:** Trivy 0.76.1, `trivy image --scanners vuln`, split by OS vs. library
  packages.
- **Tests:** full suite passes locally (36 tests) and in a clean `python:3.11-slim` container
  installed from the pinned `requirements.txt` (Streamlit 1.58.0, pillow 12.3.0).

## Reproduce

```
docker build -f deployment/docker/api.Dockerfile       -t northstar-api .
docker build -f deployment/docker/dashboard.Dockerfile -t northstar-dashboard .
docker run --rm -p 8000:8000 northstar-api            # http://localhost:8000/students/at-risk
docker run --rm -p 8501:8501 northstar-dashboard      # http://localhost:8501
trivy image --ignorefile .trivyignore.yaml northstar-dashboard
```
