"""
NorthStar knowledge agent: Microsoft Agent Framework + Azure AI Foundry +
Azure AI Search + a cross-cloud data lake over MCP, traced to Azure Monitor.

- Model: GPT-4o in the NorthStar project on Azure AI Foundry
  (FoundryChatClient, Entra ID auth through `az login`).
- Knowledge: Agent Framework's AzureAISearchContextProvider on the NorthStar
  index: hybrid search (BM25 + vectors from the same local embedding model
  the index was built with) plus Azure's semantic ranker, the configuration
  that measured best in rag_assistant/evals. Passages are labelled with
  their document name so answers can cite them.
- Data: the read-only MCP server in src/datalake_mcp, which reads the learner
  data lake from Amazon S3 (MCPStreamableHTTPTool, X-API-Key header).
- Observability: Agent Framework's OpenTelemetry spans (agent run, model
  calls, tool calls, token usage) exported to Application Insights.

    az login
    python -m knowledge_agent.agent "How many learners in Berlin are at risk?"

Settings (.env): NORTHSTAR_FOUNDRY_ENDPOINT, NORTHSTAR_FOUNDRY_MODEL,
AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, DATALAKE_MCP_URL,
DATALAKE_MCP_API_KEY, APPLICATIONINSIGHTS_CONNECTION_STRING.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

INDEX_PREFIX = "northstar-kb-"
SEMANTIC_CONFIG = "northstar-semantic"
SERVICE_NAME = "northstar-knowledge-agent"

INSTRUCTIONS = """You are the NorthStar Knowledge Agent for school leaders and staff.

Two sources, and you use only them:
1. Knowledge base passages, given to you in the conversation as "[Source: <document>] ...". Use them for how
   NorthStar works: models, rules, policies, the copilot. Cite the document for every claim, like
   (Source: early_warning_model.txt).
2. The NorthStar data lake tools (list_datasets, describe_dataset, query_dataset), which read learner data from
   Amazon S3. Use them for any number about learners: counts, averages, risk, segments, interventions, by campus,
   program, or term. Never estimate or invent a number; query it, and say which dataset it came from, like
   (Data: learners + risk_predictions).

Tool names and descriptions describe how to reach the data; they are not facts about NorthStar. Never answer a
question from them (for example, about where NorthStar's systems are hosted) unless a knowledge base passage or a
query result says so.

If neither source answers the question, reply that NorthStar's knowledge base and data don't contain it, and don't
guess. Be concise; lead with the answer."""


@dataclass
class AgentRun:
    question: str
    answer: str = ""
    tool_calls: list[dict] = field(default_factory=list)
    duration_s: float = 0.0
    usage: dict = field(default_factory=dict)
    error: str | None = None


def configure_observability() -> bool:
    """Export Agent Framework's OpenTelemetry spans to Application Insights, if configured."""
    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        return False
    from agent_framework.observability import configure_otel_providers, enable_instrumentation
    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

    configure_otel_providers(
        service_name=SERVICE_NAME,
        exporters=[AzureMonitorTraceExporter(connection_string=connection_string)],
    )
    enable_instrumentation()
    return True


_embedder = None


async def embed(text: str) -> list[float]:
    """Query embeddings from the same model the index was built with (all-MiniLM-L6-v2)."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return [float(v) for v in _embedder.encode([text])[0]]


def current_index_name() -> str:
    """The versioned NorthStar index (rag_assistant keeps exactly one current version)."""
    if os.environ.get("NORTHSTAR_SEARCH_INDEX"):
        return os.environ["NORTHSTAR_SEARCH_INDEX"]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    client = SearchIndexClient(os.environ["AZURE_SEARCH_ENDPOINT"], AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]))
    names = sorted(n for n in client.list_index_names() if n.startswith(INDEX_PREFIX))
    if len(names) != 1:
        raise RuntimeError(f"expected one {INDEX_PREFIX}* index, found {names}; set NORTHSTAR_SEARCH_INDEX")
    return names[0]


def search_provider():
    from agent_framework.azure import AzureAISearchContextProvider

    class CitedSearchProvider(AzureAISearchContextProvider):
        """Label passages with their document name, not the index's opaque id, so answers cite real sources."""

        def _extract_document_text(self, doc, doc_id=None):
            content = doc.get("content")
            return f"[Source: {doc.get('document', doc_id)}] {content}" if content else ""

    return CitedSearchProvider(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=current_index_name(),
        api_key=os.environ["AZURE_SEARCH_KEY"],
        mode="semantic",
        top_k=3,
        semantic_configuration_name=SEMANTIC_CONFIG,
        vector_field_name="embedding",
        embedding_function=embed,
        context_prompt="NorthStar knowledge base passages (cite the document for each claim):",
    )


def datalake_tool():
    from agent_framework import MCPStreamableHTTPTool

    return MCPStreamableHTTPTool(
        name="northstar_datalake",
        url=os.environ.get("DATALAKE_MCP_URL", "http://127.0.0.1:8790/mcp"),
        description="Read-only NorthStar learner data lake in Amazon S3.",
        static_headers={"X-API-Key": os.environ["DATALAKE_MCP_API_KEY"]},
        # Every tool on this server is read-only, so calls don't need human approval.
        approval_mode="never_require",
        load_prompts=False,
    )


def build_agent():
    from agent_framework import Agent
    from agent_framework.foundry import FoundryChatClient
    from azure.identity import AzureCliCredential

    client = FoundryChatClient(
        project_endpoint=os.environ["NORTHSTAR_FOUNDRY_ENDPOINT"],
        model=os.environ.get("NORTHSTAR_FOUNDRY_MODEL", "gpt-4o"),
        credential=AzureCliCredential(),
    )
    return Agent(
        client,
        instructions=INSTRUCTIONS,
        name="northstar_knowledge_agent",
        description="Answers questions about NorthStar from its knowledge base and learner data lake.",
        tools=[datalake_tool()],
        context_providers=[search_provider()],
    )


def _tool_calls(response) -> list[dict]:
    calls, results = {}, {}
    for message in response.messages:
        for content in message.contents:
            kind = getattr(content, "type", "")
            if kind == "function_call":
                calls[content.call_id] = {"name": content.name, "arguments": content.parse_arguments() or {}}
            elif kind == "function_result":
                results[content.call_id] = str(content.result)[:500]
    return [{**call, "result": results.get(call_id, "")} for call_id, call in calls.items()]


async def ask(agent, question: str) -> AgentRun:
    run = AgentRun(question=question)
    started = time.monotonic()
    try:
        response = await agent.run(question)
        run.answer = response.text
        run.tool_calls = _tool_calls(response)
        usage = getattr(response, "usage_details", None)
        run.usage = dict(usage) if usage else {}
    except Exception as exc:  # recorded, so an evaluation run continues past one failure
        run.error = f"{type(exc).__name__}: {exc}"
    run.duration_s = round(time.monotonic() - started, 2)
    return run


async def main(question: str) -> None:
    traced = configure_observability()
    # The context manager opens and closes the MCP connection in the same task.
    async with build_agent() as agent:
        run = await ask(agent, question)
    for call in run.tool_calls:
        print(f"[tool] {call['name']}({json.dumps(call['arguments'])})")
    print(run.answer or run.error)
    print(f"\n({run.duration_s}s, traces to Application Insights: {'on' if traced else 'off'})")
    print(json.dumps(asdict(run)["usage"]))


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or "What does the early warning model use to predict risk?"))
