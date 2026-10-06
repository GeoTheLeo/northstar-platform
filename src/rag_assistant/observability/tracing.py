"""
OpenTelemetry tracing for the NorthStar AI assistants.

Every assistant request produces one trace: a root span for the request,
child spans for retrieval, each LLM call, and the grounding check. LLM spans
follow the OpenTelemetry GenAI semantic conventions (gen_ai.* attributes),
so any OTLP backend (Langfuse, Arize Phoenix, Jaeger, Grafana Tempo) can
read them without custom mapping.

Spans always go to a local JSONL file (logs/traces.jsonl). Set
OTEL_EXPORTER_OTLP_ENDPOINT to also ship them to an OTLP backend.
"""

import json
import os
from pathlib import Path
from typing import Sequence

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.trace import Tracer

PROJECT_ROOT = Path(__file__).resolve().parents[3]

TRACE_LOG_PATH = PROJECT_ROOT / "logs" / "traces.jsonl"

SERVICE_NAME = "northstar-ai-assistant"

# USD per 1M tokens. Update when provider pricing changes.
MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

_provider: TracerProvider | None = None


class JsonlSpanExporter(SpanExporter):
    """
    Appends finished spans to a JSONL file, one span per line.
    """

    def __init__(self, path: Path = TRACE_LOG_PATH) -> None:

        self.path = path

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.path, "a", encoding="utf-8") as file:
                for span in spans:
                    file.write(json.dumps(span_to_dict(span)) + "\n")

        except OSError:
            return SpanExportResult.FAILURE

        return SpanExportResult.SUCCESS


def span_to_dict(span: ReadableSpan) -> dict:
    """
    Flatten a finished span into a JSON-serialisable dict.
    """

    context = span.get_span_context()

    start = span.start_time or 0
    end = span.end_time or start

    return {
        "name": span.name,
        "trace_id": format(context.trace_id, "032x") if context else None,
        "span_id": format(context.span_id, "016x") if context else None,
        "parent_span_id": (
            format(span.parent.span_id, "016x") if span.parent else None
        ),
        "start_time_unix_nano": start,
        "duration_ms": round((end - start) / 1e6, 2),
        "status": span.status.status_code.name,
        "attributes": dict(span.attributes or {}),
    }


def configure_tracing(exporters: Sequence[SpanExporter] | None = None) -> TracerProvider:
    """
    (Re)build the tracer provider. Tests pass their own exporters; the app
    uses the defaults: local JSONL, plus OTLP when an endpoint is configured.
    """

    global _provider

    provider = TracerProvider(
        resource=Resource.create({"service.name": SERVICE_NAME}),
    )

    if exporters is not None:
        for exporter in exporters:
            provider.add_span_processor(SimpleSpanProcessor(exporter))

    else:
        provider.add_span_processor(SimpleSpanProcessor(JsonlSpanExporter()))

        if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

    _provider = provider

    return provider


def get_tracer() -> Tracer:
    """
    Tracer for the assistant. Uses a dedicated provider rather than the
    global one, so it never clashes with tracing set up by a host app.
    """

    if _provider is None:
        configure_tracing()

    assert _provider is not None

    return _provider.get_tracer("northstar.rag_assistant")


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float | None:
    """
    Estimated request cost from token usage, or None for unpriced models.
    """

    pricing = MODEL_PRICING.get(model)

    if pricing is None:
        return None

    return (
        input_tokens * pricing["input"] + output_tokens * pricing["output"]
    ) / 1_000_000
