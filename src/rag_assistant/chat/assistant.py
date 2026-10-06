"""
NorthStar Knowledge Assistant.

Routes user questions to the appropriate retrieval
or executive briefing workflow.
"""

import time

from rag_assistant.chat.answer_generator import (
    AnswerResult,
    answer_question,
    format_answer,
)
from rag_assistant.chat.copilot import (
    generate_executive_brief,
)
from rag_assistant.ingestion.document_loader import (
    load_live_metrics_chunk,
)
from rag_assistant.observability.tracing import get_tracer
from rag_assistant.retrieval.retriever import (
    get_index,
)
from rag_assistant.vectorstore.qdrant_store import KnowledgeIndex

BRIEFING_TRIGGERS = (
    "executive briefing",
    "executive summary",
    "platform status",
)


def answer_with_rag(
    question: str,
    index: KnowledgeIndex | None = None,
    include_live_metrics: bool = True,
    top_k: int = 3,
) -> AnswerResult:
    """
    Retrieve, generate, and verify one answer inside a single trace.
    """

    index = index or get_index()

    with get_tracer().start_as_current_span("rag.ask") as root:

        started = time.perf_counter()

        root.set_attribute("northstar.rag.question_chars", len(question))

        if include_live_metrics:
            index.upsert([load_live_metrics_chunk()])

        with get_tracer().start_as_current_span("rag.retrieve") as span:

            results = index.search(question, top_k=top_k)

            span.set_attribute("db.system.name", "qdrant")
            span.set_attribute("db.collection.name", index.collection)
            span.set_attribute("northstar.rag.top_k", top_k)
            span.set_attribute(
                "northstar.rag.top_score",
                results[0]["score"] if results else 0.0,
            )
            span.set_attribute(
                "northstar.rag.retrieved_documents",
                [r["document"] for r in results],
            )

        result = answer_question(question, results)

        result.latency_ms = round((time.perf_counter() - started) * 1000, 1)
        result.trace_id = format(root.get_span_context().trace_id, "032x")

        root.set_attribute("northstar.rag.status", result.status)
        root.set_attribute("northstar.llm.total_cost_usd", result.cost_usd)
        root.set_attribute("gen_ai.usage.input_tokens", result.input_tokens)
        root.set_attribute("gen_ai.usage.output_tokens", result.output_tokens)

        return result


def ask_assistant(question: str) -> str:
    """
    Answer a user question using either the executive
    copilot or the RAG pipeline.
    """

    question_lower = question.lower()

    if any(trigger in question_lower for trigger in BRIEFING_TRIGGERS):
        return generate_executive_brief()

    return format_answer(answer_with_rag(question))
