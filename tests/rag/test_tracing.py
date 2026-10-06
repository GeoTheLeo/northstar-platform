"""
OpenTelemetry tracing of assistant requests.
"""

import json

from rag_assistant.chat.assistant import answer_with_rag
from rag_assistant.observability.tracing import (
    JsonlSpanExporter,
    configure_tracing,
    estimate_cost_usd,
    get_tracer,
)

GROUNDED = json.dumps({"grounded": True, "unsupported_claims": []})


def test_request_produces_one_trace_with_nested_spans(knowledge_index, spans, fake_llm):

    fake_llm(["It uses a Random Forest [1].", GROUNDED])

    result = answer_with_rag(
        "What model does the early warning system use?",
        index=knowledge_index,
        include_live_metrics=False,
    )

    finished = {span.name: span for span in spans.get_finished_spans()}

    assert {"rag.ask", "rag.retrieve", "rag.generate"} <= set(finished)

    root = finished["rag.ask"]

    assert {span.context.trace_id for span in finished.values()} == {root.context.trace_id}
    assert finished["rag.retrieve"].parent.span_id == root.context.span_id
    assert format(root.context.trace_id, "032x") == result.trace_id

    assert finished["rag.retrieve"].attributes["db.system.name"] == "qdrant"
    assert finished["rag.retrieve"].attributes["northstar.rag.top_score"] > 0.25
    assert root.attributes["northstar.rag.status"] == "answered"
    assert root.attributes["gen_ai.usage.input_tokens"] == 200
    assert result.latency_ms is not None


def test_off_topic_request_is_traced_without_llm_spans(knowledge_index, spans, fake_llm):

    fake = fake_llm([])

    answer_with_rag("Write me a poem about the ocean.", index=knowledge_index, include_live_metrics=False)

    names = [span.name for span in spans.get_finished_spans()]

    assert fake.calls == []
    assert not any(name.startswith("chat ") for name in names)
    assert "rag.ask" in names


def test_jsonl_exporter_writes_one_line_per_span(tmp_path):

    path = tmp_path / "traces.jsonl"

    configure_tracing([JsonlSpanExporter(path)])

    with get_tracer().start_as_current_span("outer"):
        with get_tracer().start_as_current_span("inner") as inner:
            inner.set_attribute("gen_ai.usage.input_tokens", 42)

    configure_tracing([])

    lines = [json.loads(line) for line in path.read_text().splitlines()]

    assert [line["name"] for line in lines] == ["inner", "outer"]
    assert lines[0]["parent_span_id"] == lines[1]["span_id"]
    assert lines[0]["attributes"]["gen_ai.usage.input_tokens"] == 42


def test_cost_estimate():

    assert estimate_cost_usd("gpt-4o-mini", 1_000_000, 1_000_000) == 0.75
    assert estimate_cost_usd("unknown-model", 10, 10) is None
