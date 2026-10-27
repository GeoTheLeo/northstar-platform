# NorthStar Knowledge Agent

A knowledge agent for school leaders and staff, built on **Microsoft Agent Framework**, **Azure AI Foundry**, and
**Azure AI Search**, that also reads learner data from an **AWS S3 data lake** through a read-only **MCP** server,
with **OpenTelemetry** monitoring in **Azure Monitor** and a scripted evaluation run.

This document follows a delivery write-up: solution, deployment approach, assumptions, limitations, and findings.

## Solution

```
question
  └─ Agent Framework Agent (northstar_knowledge_agent)          Azure AI Foundry: GPT-4o, NorthStar project
       ├─ AzureAISearchContextProvider ──► Azure AI Search     knowledge base: hybrid (BM25 + vectors)
       │      passages labelled [Source: <document>]           + semantic ranker, top 3
       ├─ MCPStreamableHTTPTool ──► datalake_mcp server ──► Amazon S3 (Parquet)   read-only, X-API-Key
       │      list_datasets / describe_dataset / query_dataset
       └─ OpenTelemetry ──► Application Insights (Azure Monitor)
```

| Part | Where | What it does |
|---|---|---|
| Agent | `agent.py` | `Agent` + `FoundryChatClient` (Entra ID via `az login`); instructions require a cited document for every knowledge claim, a named dataset for every number, and a refusal when neither source answers |
| Knowledge | `agent.py` (`CitedSearchProvider`) | Agent Framework's `AzureAISearchContextProvider` on the NorthStar index (same chunks and embeddings as `rag_assistant`), hybrid + semantic ranker: the configuration that measured best in `rag_assistant/evals`. The subclass labels passages with their document name instead of the index's opaque id, so citations are readable |
| Cross-cloud data | `../datalake_mcp/server.py` | MCP server reading Parquet from `s3://$DATALAKE_BUCKET/northstar/` with boto3. Three read-only tools; queries are a validated JSON spec (joins on `learner_id`, filters, group-by, aggregates, sorting, row cap), not SQL |
| Data lake contents | `../datalake_mcp/build_datalake.py` | 2,000 synthetic, seeded learners (6 campuses, 3 programs, 2 terms). `at_risk` comes from NorthStar's own early-warning Random Forest, `segment` from its KMeans pipeline; interventions are synthetic |
| Monitoring | `agent.py` (`configure_observability`) | Agent Framework's OpenTelemetry spans and metrics exported to Application Insights: `invoke_agent`, `chat gpt-4o`, `execute_tool`, and the MCP client calls, with token usage |
| Evaluation | `evals/run_evals.py` | 40 scenarios, deterministic grading, JSON report in `evals/results/` |

## Deployment approach

Infrastructure is Bicep:

| Resource | File | Notes |
|---|---|---|
| Azure AI Search (Free, North Europe) | `infra/search.bicep` | Sweden Central and Germany West Central were out of capacity |
| Foundry project "NorthStar Knowledge Agent" | `infra/foundry-project.bicep` | On the Foundry resource from `music_man/infra/foundry.bicep` (GPT-4o, Entra-only auth) |
| Application Insights + Log Analytics | `infra/monitoring.bicep` | Workspace-based, 30-day retention |

```bash
pip install -r requirements.txt                                # main environment
python src/datalake_mcp/build_datalake.py --upload <bucket>     # build the lake, upload to S3

python -m venv .venv-agent                                     # agent environment (isolated from the app)
.venv-agent/Scripts/pip install agent-framework==1.23.0 boto3 pandas pyarrow uvicorn python-dotenv \
    sentence-transformers==5.6.0 azure-search-documents==12.0.0 azure-monitor-opentelemetry-exporter
az login
DATALAKE_BUCKET=<bucket> python -m datalake_mcp.server --http 8790 --host 0.0.0.0   # needs DATALAKE_MCP_API_KEY
python -m knowledge_agent.agent "How many learners in Berlin are at risk?"
```

Settings live in `.env` (git-ignored): `NORTHSTAR_FOUNDRY_ENDPOINT`, `NORTHSTAR_FOUNDRY_MODEL`,
`AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`, `DATALAKE_MCP_URL`, `DATALAKE_MCP_API_KEY`,
`APPLICATIONINSIGHTS_CONNECTION_STRING`.

**AWS access is read-only by policy as well as by code.** The MCP server's IAM principal needs only:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": "s3:ListBucket", "Resource": "arn:aws:s3:::<bucket>",
     "Condition": {"StringLike": {"s3:prefix": "northstar/*"}}},
    {"Effect": "Allow", "Action": "s3:GetObject", "Resource": "arn:aws:s3:::<bucket>/northstar/*"}
  ]
}
```

In production the MCP server runs next to the agent in Azure (for example on Azure Container Apps, like
`music_man`'s MCP server), with the AWS credentials held as a Container Apps secret, or, better, AWS IAM roles
anywhere / workload identity federation so no long-lived AWS key exists.

## Assumptions

- The knowledge base is NorthStar's eight documents, indexed by `rag_assistant` (22 chunks).
- The learner data is a synthetic, seeded cohort; risk and segment values come from NorthStar's real models.
- Questions are single-turn. Each evaluation scenario is a fresh conversation.
- Numbers are always read from the data lake at question time; the agent never answers a number from memory.

## Limitations

- **AWS not yet connected live.** The MCP server uses the real S3 API through boto3, and the IAM policy above is
  ready, but the evaluation ran against an S3-compatible stand-in (moto, `local_datalake.py`) because no AWS
  account was available. Switching is credentials plus `DATALAKE_BUCKET`; no code changes.
- **Microsoft Agent 365 is not configured.** It needs Microsoft 365 licensing this tenant doesn't have.
  Monitoring uses OpenTelemetry into Application Insights, which carries the same span data (agent invocations,
  model calls, tool calls, tokens).
- **Small knowledge base.** Eight documents; retrieval quality was measured separately in `rag_assistant/evals`.
- **Deterministic grading is strict.** A correct answer worded differently from the expected phrase is a fail;
  see Findings for the two cases this caused.
- **Cold start.** The first question loads the local embedding model (about 10 s); later questions take a few
  seconds.

## Findings

**Evaluation (2026-10-27, GPT-4o, 40 scenarios):**

| Scenario | First run | After fixes | Notes |
|---|---|---|---|
| Knowledge (fact + citation) | 19/20 | 19/20 | The one fail is a correct answer that paraphrased the expected phrase |
| Refusal (off-topic, near-domain) | 9/10 | 9/10 | Run 2's fail is a correct refusal worded "not specified", which the grader doesn't match |
| Data (computed ground truth) | 7/8 | **8/8** | |
| Mixed (knowledge + data) | 2/2 | 2/2 | |
| **Total, automated** | **37/40** | **38/40** | Manual review of run 2: both fails are correct behavior |
| Median / p95 latency | 2.4 s / 16.7 s | 2.3 s / 7.8 s | |
| Cost (GPT-4o list price) | $0.14 | $0.16 | For all 40 questions |

The grader was not loosened after seeing results, so the automated score stays strict.

**Two real defects found and fixed by the first run:**

1. **"Top N" returned the wrong group.** Asked which program has the most at-risk learners, the agent queried
   with `limit: 1`; the server returned grouped rows in alphabetical order, so the agent answered "Business
   English (220)" instead of "General English (417)". Grouped results are now sorted by the metric, largest first,
   with an explicit `order_by` option and a regression test.
2. **Tool metadata treated as a fact.** Asked which cloud provider hosts the NorthStar database, the agent answered
   "Amazon S3" with an invented citation, inferring it from the MCP tool descriptions. The instructions now state
   that tool descriptions are not facts about NorthStar; the question is refused in run 2.

**From the traces:** a data-lake query takes about 90 ms end to end (`execute_tool query_dataset`); nearly all of a
question's latency is the model (`chat gpt-4o`, about 2.7 s per call).
