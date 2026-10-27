"""
The knowledge agent's wiring and evaluation grader, offline (no Azure calls).
Runs in .venv-agent; skipped where Microsoft Agent Framework isn't installed.
"""

import pytest

pytest.importorskip("agent_framework")

from knowledge_agent import agent as ka  # noqa: E402
from knowledge_agent.agent import AgentRun  # noqa: E402
from knowledge_agent.evals import run_evals  # noqa: E402


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://example.search.windows.net")
    monkeypatch.setenv("AZURE_SEARCH_KEY", "test")
    monkeypatch.setenv("NORTHSTAR_SEARCH_INDEX", "northstar-kb-test")
    monkeypatch.setenv("DATALAKE_MCP_API_KEY", "secret-key")
    monkeypatch.setenv("DATALAKE_MCP_URL", "http://127.0.0.1:8790/mcp")


def test_passages_are_labelled_with_their_document_name():
    provider = ka.search_provider()
    text = provider._extract_document_text({"id": "9f2c", "document": "early_warning_model.txt", "content": "100 trees."})
    assert text == "[Source: early_warning_model.txt] 100 trees."
    assert provider.semantic_configuration_name == ka.SEMANTIC_CONFIG
    assert provider.vector_field_name == "embedding"


def test_datalake_tool_sends_the_key_and_needs_no_approval():
    tool = ka.datalake_tool()
    assert tool.url == "http://127.0.0.1:8790/mcp"
    assert dict(tool._static_headers)["X-API-Key"] == "secret-key"
    assert tool.approval_mode == "never_require"  # every data lake tool is read-only


def test_instructions_require_citations_data_sources_and_refusals():
    text = ka.INSTRUCTIONS
    assert "Cite the document" in text and "Never estimate or invent a number" in text
    assert "not facts about NorthStar" in text


def _run(answer, tools=()):
    return AgentRun(question="q", answer=answer, tool_calls=[{"name": t, "arguments": {}} for t in tools])


def test_data_grading_needs_the_number_the_query_and_the_source():
    case = {"question": "q", "expected": 127}
    assert run_evals.grade("data", case, _run("127 learners (Data: learners + risk_predictions)", ["query_dataset"]))["passed"]
    assert not run_evals.grade("data", case, _run("126 learners (Data: learners)", ["query_dataset"]))["passed"]
    assert not run_evals.grade("data", case, _run("127 learners (Data: learners)"))["passed"]  # no query: a guess


def test_knowledge_grading_needs_facts_and_the_cited_document():
    case = {"question": "q", "must_include": ["random forest"], "expected_document": "early_warning_model.txt"}
    assert run_evals.grade("knowledge", case, _run("A Random Forest (Source: early_warning_model.txt)"))["passed"]
    assert not run_evals.grade("knowledge", case, _run("A Random Forest."))["passed"]


def test_refusal_grading():
    case = {"question": "q"}
    assert run_evals.grade("refusal", case, _run("NorthStar's knowledge base and data don't contain that."))["passed"]
    assert not run_evals.grade("refusal", case, _run("Paris."))["passed"]
