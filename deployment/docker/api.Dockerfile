# syntax=docker/dockerfile:1.7
#
# NorthStar inference API (services/copilot_api).
# Build from the repo root:
#   docker build -f deployment/docker/api.Dockerfile -t northstar-api .

# ---- builder: resolve and install dependencies into a venv ---------------
FROM python:3.11-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY requirements/api.txt /tmp/api.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/api.txt \
    && pip uninstall -y pip setuptools wheel

# ---- runtime: venv + only the code and data the API reads ----------------
FROM python:3.11-slim

# Packaging tools are never used at runtime but carry their own CVEs.
RUN python -m pip uninstall -y pip setuptools wheel \
    && useradd --uid 10001 --create-home --shell /usr/sbin/nologin northstar

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY services/ services/
COPY src/northstar/ src/northstar/
COPY data/raw/student_data.csv data/raw/student_data.csv
RUN mkdir -p logs && chown northstar:northstar logs

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONPATH=/app/src:/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER 10001
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

CMD ["uvicorn", "services.copilot_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
