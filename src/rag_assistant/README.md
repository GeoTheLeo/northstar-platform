# NorthStar Knowledge Assistant (RAG)

Retrieval-augmented assistant behind the **Knowledge Assistant** page of the
NorthStar dashboard. It answers questions about the platform from a small
knowledge base plus live platform metrics, and is built to refuse rather
than guess.

## Pipeline

```
question
  └─ rag.ask (root span)
       ├─ upsert live platform metrics into the index
       ├─ rag.retrieve      Qdrant hybrid search: dense + BM25 candidates fused by
       │                    reciprocal rank, reranked by a cross-encoder, top 3
       └─ rag.generate
            ├─ 1. relevance gate     best cosine score < 0.25 → "I don't know", no LLM call
            ├─ 2. cited generation   answer from numbered context, cite [n] per claim,
            │                        or reply NOT_IN_KNOWLEDGE_BASE
            └─ 3. grounding check    temperature-0 LLM judge; unsupported → withheld,
                                     relevant passages shown instead
```

| Module | Role |
|---|---|
| `vectorstore/qdrant_store.py` | Qdrant index. Embedded on local disk by default; set `QDRANT_URL` (+ `QDRANT_API_KEY`) for a Qdrant server or Qdrant Cloud. The collection name carries a content and schema fingerprint, so editing a document re-indexes and an unchanged knowledge base is reused across restarts. Each chunk has a dense embedding (with its document title as a header: contextual retrieval) and a BM25 sparse vector. `search()` runs dense or hybrid retrieval, with optional reranking; hybrid + rerank is the default. |
| `vectorstore/azure_search_store.py` | **Azure AI Search** backend with the same interface (`RAG_BACKEND=azure_search`, `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`; `pip install -r requirements-azure.txt`). Same local embeddings pushed as vectors; modes: vector, hybrid (BM25 + vector, RRF), and hybrid + Azure's semantic ranker (the default on this backend). `infra/search.bicep` creates the service. |
| `vectorstore/sparse.py` | BM25 sparse vectors: term-frequency weights per chunk, IDF applied by Qdrant, CRC32 term ids that are stable across restarts. |
| `retrieval/reranker.py` | Cross-encoder reranking (`ms-marco-MiniLM-L6-v2`, local, loaded on first use). |
| `ingestion/chunker.py` | Paragraph-aware chunking, so a rule and its consequence never split across chunks. |
| `chat/answer_generator.py` | The three guardrails; returns an auditable `AnswerResult` (status, sources, grounding verdict, tokens, cost, trace ID). |
| `llm.py` | Single traced LLM client shared by the assistant and the Executive Copilot. |
| `observability/tracing.py` | OpenTelemetry tracing, GenAI semantic conventions. |
| `evals/` | Golden set and evaluation runner. |

## Observability

Every request is one OpenTelemetry trace. LLM spans use the GenAI semantic
conventions (`gen_ai.request.model`, `gen_ai.usage.input_tokens`,
`gen_ai.usage.output_tokens`, …) plus an estimated cost per call; retrieval
spans record the retrieval mode, whether reranking ran, the best similarity
score, and the documents retrieved.

- Spans are always appended to `logs/traces.jsonl`.
- Set `OTEL_EXPORTER_OTLP_ENDPOINT` to also export over OTLP/HTTP to any
  compatible backend (Langfuse, Arize Phoenix, Jaeger, Grafana Tempo).
- In the dashboard, each answer has an **Answer trace** panel with status,
  grounding verdict, retrieval scores, latency, tokens, cost, and trace ID.

## Evaluation

```
python src/rag_assistant/evals/run_evals.py            # retrieval only, no API key
python src/rag_assistant/evals/run_evals.py --compare  # dense vs. hybrid, with/without reranking
python src/rag_assistant/evals/run_evals.py --e2e      # full pipeline, needs OPENAI_API_KEY
```

The golden set has 20 answerable questions (expected source document and
required facts) and 10 unanswerable ones: 5 off-topic and 5 deliberately
near-domain (e.g. "What is the accuracy of the early warning model on the
test set?"), which pass the relevance gate and test the model's refusal.
A third slice has 14 short keyword queries of the kind people type into a
search box ("80/20 split", "Platform Healthy", "BI Decision Command
Center"), written before hybrid search existed. Results are written to
`evals/results/latest.json`.

### Hybrid retrieval and reranking (2026-10-21)

`--compare`, retrieval only (no LLM), top 3; per-question results in
`evals/results/retrieval_comparison_2026-10-21.json`:

| Metric | Dense | Dense + rerank | Hybrid | **Hybrid + rerank** |
|---|---|---|---|---|
| Questions hit@1 / hit@3 | 95% / 100% | 95% / 100% | 90% / 100% | **95% / 100%** |
| Keyword queries hit@1 | 79% | 93% | 93% | **100%** |
| Keyword queries hit@3 | 93% | 93% | 100% | **100%** |
| Keyword queries MRR | 0.845 | 0.929 | 0.952 | **1.000** |
| Answerable above gate / off-topic gated | 100% / 100% | 100% / 100% | 100% / 100% | **100% / 100%** |
| Mean latency per query (CPU) | 11 ms | 104 ms | 11 ms | 112 ms |

- Hybrid + rerank is the best or tied-best configuration on every quality
  metric, so it's the default. The cost is about 0.1 s per question for the
  cross-encoder, against an LLM pipeline that takes ~2.5 s.
- The gains are on exact terms. "Platform Healthy" names a rule in the
  advisor document, but its embedding sits closer to the platform overview,
  and dense retrieval doesn't return the rule in the top 3. BM25 brings it
  into the candidates, and the reranker puts it first.
- Hybrid without reranking is slightly worse on full questions (90% hit@1):
  the keyword half can promote a chunk that shares words but not meaning.
  The reranker removes that regression, so they ship together.
- On full questions the knowledge base is too small (22 chunks) for either
  technique to show a lift; the one remaining hit@1 miss ("How does
  NorthStar support student success?") is ambiguous between two documents in
  every configuration.
- The relevance gate still uses cosine similarity, now the best score among
  the retrieved chunks rather than the first: after reranking, the right
  chunk can come first with a low cosine score ("Platform Healthy": 0.06,
  while the gate's 0.25 is cleared by another retrieved chunk). Checking only
  the first chunk would have refused that correct answer.

### Azure AI Search (2026-10-26)

`--compare --backend azure_search` on the same golden set, against an Azure
AI Search index (Free tier, North Europe) holding the same chunks and
embeddings. Per-question results in
`evals/results/retrieval_comparison_azure_2026-10-26.json`:

| Metric | Vector | Hybrid | Hybrid + local cross-encoder | **Hybrid + Azure semantic ranker** |
|---|---|---|---|---|
| Questions hit@1 / hit@3 | 95% / 100% | 100% / 100% | 95% / 100% | **95% / 100%** |
| Keyword queries hit@1 | 79% | 93% | 100% | **100%** |
| Keyword queries MRR | 0.845 | 0.929 | 1.000 | **1.000** |
| Answerable above gate / off-topic gated | 100% / 100% | 100% / 100% | 100% / 100% | **100% / 100%** |
| Mean latency per query | 65 ms | 71 ms | 176 ms | **103 ms** |

- Vector-only results match the Qdrant backend exactly, as they should with
  the same embeddings: the comparison isolates the search engine.
- Azure's hybrid search alone did better on full questions than Qdrant's
  hybrid (100% vs. 90% hit@1).
- Azure's semantic ranker matched the local cross-encoder on every quality
  metric at about 40% lower latency and with no reranking model to ship, so
  hybrid + semantic ranker is the default on this backend.
- The live regression test (`tests/rag/test_azure_search.py`) runs when the
  Azure credentials are set and is skipped otherwise.

### End-to-end

Last end-to-end run (2026-10-06, gpt-4o-mini, all-MiniLM-L6-v2, dense
retrieval; not yet re-run with hybrid + rerank):

| Metric | Result |
|---|---|
| Retrieval hit@1 / hit@3 | 95% / 100% |
| Answer correctness (required facts present) | 100% |
| False refusals | 0% |
| Answered responses passing the grounding check | 100% |
| Unanswerable questions refused | 100% (5 by relevance gate, 5 by model refusal) |
| Hallucinated answers | 0 |
| Latency median / p95 | ~2.5 s / ~3.8 s |
| Cost for all 30 questions | ~$0.002 |

How it got there: the first end-to-end run scored 85% correctness with 15%
false refusals. The traces showed the model was right to refuse: fixed
3-sentence chunks had split rules from their consequences, and title-less
paragraphs ("The model is a Random Forest…") lost to vaguer intro sentences
that named the topic. Paragraph-aware chunking plus document-title headers
on embeddings brought it to 95%; the last miss was a vocabulary gap in the
knowledge base itself ("4 clusters" vs. "segments"), fixed in the document.

The retrieval metrics run in CI as a regression gate
(`tests/rag/test_vector_store.py`, and `tests/rag/test_hybrid_retrieval.py`
for the keyword slice, cosine scores across modes, and the best-score gate); the guardrail and tracing behaviour is
covered with a scripted fake LLM (`tests/rag/test_guardrails.py`,
`tests/rag/test_tracing.py`), including the ungrounded-answer path that the
golden set doesn't trigger.
