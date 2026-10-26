# syntax=docker/dockerfile:1.7
#
# NorthStar Streamlit dashboard, including the in-process Knowledge Assistant (RAG).
# Build from the repo root:
#   docker build -f deployment/docker/dashboard.Dockerfile -t northstar-dashboard .

# ---- builder: dependencies + pre-downloaded RAG models -------------------
FROM python:3.11-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

# CPU-only torch first. On Linux, plain `pip install torch` pulls the CUDA build
# (several GB of nvidia-* wheels) that a CPU pod can never use.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt

# Bake the embedding and reranker models into the image so a new pod never
# downloads them from Hugging Face at startup.
ENV HF_HOME=/opt/hf
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('all-MiniLM-L6-v2'); \
CrossEncoder('cross-encoder/ms-marco-MiniLM-L6-v2')"

RUN pip uninstall -y pip setuptools wheel

# ---- runtime -------------------------------------------------------------
FROM python:3.11-slim

# Packaging tools are never used at runtime but carry their own CVEs.
RUN python -m pip uninstall -y pip setuptools wheel \
    && useradd --uid 10001 --create-home --shell /usr/sbin/nologin northstar

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/hf /opt/hf

WORKDIR /app
COPY src/ src/
COPY data/ data/
COPY models/ models/
COPY assets/ assets/
COPY docs/ docs/
# The app writes its log, traces, DuckDB warehouse and vector index at runtime.
RUN mkdir -p logs data/warehouse data/vector_store \
    && chown -R northstar:northstar logs data

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/opt/hf \
    HF_HUB_OFFLINE=1

USER 10001
EXPOSE 8501

HEALTHCHECK --interval=15s --timeout=3s --start-period=60s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=2)"]

CMD ["streamlit", "run", "src/northstar/app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.headless=true", "--browser.gatherUsageStats=false"]
