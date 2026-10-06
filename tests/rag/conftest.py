"""
Shared fixtures for the RAG assistant tests.
"""

import pytest
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from rag_assistant import llm
from rag_assistant.ingestion.document_loader import load_document_chunks
from rag_assistant.observability.tracing import configure_tracing
from rag_assistant.vectorstore.qdrant_store import KnowledgeIndex, make_client


@pytest.fixture(scope="session")
def knowledge_index():
    """
    The real knowledge base in an in-memory Qdrant collection.
    """

    return KnowledgeIndex(load_document_chunks(), make_client(":memory:"))


@pytest.fixture
def spans():
    """
    Capture spans in memory instead of writing logs/traces.jsonl.
    """

    exporter = InMemorySpanExporter()

    configure_tracing([exporter])

    yield exporter

    configure_tracing([])


class FakeLLM:
    """
    Scripted stand-in for llm.chat: returns queued replies in order and
    records every call, so tests can assert when the LLM was (not) used.
    """

    def __init__(self, replies):

        self.replies = list(replies)

        self.calls = []

    def __call__(self, messages, temperature=0.2, json_output=False, purpose="generation"):

        self.calls.append(purpose)

        reply = self.replies.pop(0)

        if isinstance(reply, Exception):
            raise reply

        return llm.LLMResponse(
            text=reply,
            input_tokens=100,
            output_tokens=20,
            cost_usd=0.0001,
        )


@pytest.fixture
def fake_llm(monkeypatch):
    """
    Factory: fake_llm(["reply 1", "reply 2"]) patches llm.chat.
    """

    def install(replies):

        fake = FakeLLM(replies)

        monkeypatch.setattr(llm, "chat", fake)

        return fake

    return install
