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
       ├─ rag.retrieve      Qdrant top-3 by cosine similarity
       └─ rag.generate
            ├─ 1. relevance gate     top score < 0.25 → "I don't know", no LLM call
            ├─ 2. cited generation   answer from numbered context, cite [n] per claim,
            │                        or reply NOT_IN_KNOWLEDGE_BASE
            └─ 3. grounding check    temperature-0 LLM judge; unsupported → withheld,
                                     relevant passages shown instead
```

| Module | Role |
|---|---|
| `vectorstore/qdrant_store.py` | Qdrant index. Embedded on local disk by default; set `QDRANT_URL` (+ `QDRANT_API_KEY`) for a Qdrant server or Qdrant Cloud. The collection name carries a content fingerprint, so editing a document re-indexes and an unchanged knowledge base is reused across restarts. Chunks are embedded with their document title as a header (contextual retrieval). |
| `ingestion/chunker.py` | Paragraph-aware chunking, so a rule and its consequence never split across chunks. |
| `chat/answer_generator.py` | The three guardrails; returns an auditable `AnswerResult` (status, sources, grounding verdict, tokens, cost, trace ID). |
| `llm.py` | Single traced LLM client shared by the assistant and the Executive Copilot. |
| `observability/tracing.py` | OpenTelemetry tracing, GenAI semantic conventions. |
| `evals/` | Golden set and evaluation runner. |

## Observability

Every request is one OpenTelemetry trace. LLM spans use the GenAI semantic
conventions (`gen_ai.request.model`, `gen_ai.usage.input_tokens`,
`gen_ai.usage.output_tokens`, …) plus an estimated cost per call; retrieval
spans record the top similarity score and the documents retrieved.

- Spans are always appended to `logs/traces.jsonl`.
- Set `OTEL_EXPORTER_OTLP_ENDPOINT` to also export over OTLP/HTTP to any
  compatible backend (Langfuse, Arize Phoenix, Jaeger, Grafana Tempo).
- In the dashboard, each answer has an **Answer trace** panel with status,
  grounding verdict, retrieval scores, latency, tokens, cost, and trace ID.

## Evaluation

```
python src/rag_assistant/evals/run_evals.py          # retrieval only, no API key
python src/rag_assistant/evals/run_evals.py --e2e    # full pipeline, needs OPENAI_API_KEY
```

The golden set has 20 answerable questions (expected source document and
required facts) and 10 unanswerable ones: 5 off-topic and 5 deliberately
near-domain (e.g. "What is the accuracy of the early warning model on the
test set?"), which pass the relevance gate and test the model's refusal.
Results are written to `evals/results/latest.json`.

Latest run (gpt-4o-mini, all-MiniLM-L6-v2):

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
(`tests/rag/test_vector_store.py`); the guardrail and tracing behaviour is
covered with a scripted fake LLM (`tests/rag/test_guardrails.py`,
`tests/rag/test_tracing.py`), including the ungrounded-answer path that the
golden set doesn't trigger.
