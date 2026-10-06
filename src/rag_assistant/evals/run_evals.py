"""
NorthStar RAG evaluation.

Retrieval stage (no LLM, runs in CI via tests/rag):
  - hit@1 / hit@3 for answerable questions
  - top-score separation between answerable and off-topic questions,
    used to calibrate MIN_RELEVANCE

End-to-end stage (--e2e, needs OPENAI_API_KEY):
  - answer correctness (required facts present), groundedness, false refusals
  - refusal rate on unanswerable questions, split by which guardrail caught it
  - latency, tokens, and cost per question

Run from the repository root:
    python src/rag_assistant/evals/run_evals.py [--e2e]
"""

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

sys.path.append(str(PROJECT_ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from rag_assistant.chat.answer_generator import (  # noqa: E402
    MIN_RELEVANCE,
    STATUS_ANSWERED,
    STATUS_LOW_RELEVANCE,
    STATUS_NOT_IN_KB,
    STATUS_UNGROUNDED,
)
from rag_assistant.ingestion.document_loader import load_document_chunks  # noqa: E402
from rag_assistant.vectorstore.qdrant_store import KnowledgeIndex, make_client  # noqa: E402

GOLDEN_SET_PATH = Path(__file__).with_name("golden_set.json")

RESULTS_DIR = Path(__file__).with_name("results")

REFUSED = {STATUS_LOW_RELEVANCE, STATUS_NOT_IN_KB}


def load_golden_set() -> dict:

    return json.loads(GOLDEN_SET_PATH.read_text(encoding="utf-8"))


def build_index() -> KnowledgeIndex:
    """
    Fresh in-memory index, so evals never touch the app's local store.
    """

    return KnowledgeIndex(load_document_chunks(), make_client(":memory:"))


def evaluate_retrieval(index: KnowledgeIndex, golden: dict, top_k: int = 3) -> dict:

    answerable = []

    for case in golden["answerable"]:

        results = index.search(case["question"], top_k=top_k)
        documents = [r["document"] for r in results]

        answerable.append(
            {
                "question": case["question"],
                "top_score": results[0]["score"],
                "hit_at_1": documents[:1] == [case["expected_document"]],
                "hit_at_k": case["expected_document"] in documents,
            }
        )

    unanswerable = []

    for case in golden["unanswerable"]:

        results = index.search(case["question"], top_k=top_k)

        unanswerable.append(
            {
                "question": case["question"],
                "kind": case["kind"],
                "top_score": results[0]["score"],
                "gated": results[0]["score"] < MIN_RELEVANCE,
            }
        )

    answerable_scores = [a["top_score"] for a in answerable]
    off_topic_scores = [u["top_score"] for u in unanswerable if u["kind"] == "off_topic"]

    return {
        "hit_at_1": sum(a["hit_at_1"] for a in answerable) / len(answerable),
        f"hit_at_{top_k}": sum(a["hit_at_k"] for a in answerable) / len(answerable),
        "min_answerable_score": min(answerable_scores),
        "max_off_topic_score": max(off_topic_scores),
        "answerable_above_threshold": sum(s >= MIN_RELEVANCE for s in answerable_scores)
        / len(answerable_scores),
        "off_topic_gated": sum(s < MIN_RELEVANCE for s in off_topic_scores)
        / len(off_topic_scores),
        "threshold": MIN_RELEVANCE,
        "answerable": answerable,
        "unanswerable": unanswerable,
    }


def evaluate_end_to_end(index: KnowledgeIndex, golden: dict) -> dict:

    from rag_assistant.chat.assistant import answer_with_rag

    rows = []

    for case in golden["answerable"]:

        result = answer_with_rag(case["question"], index=index, include_live_metrics=False)

        rows.append(
            {
                "question": case["question"],
                "expected": "answer",
                "status": result.status,
                "correct": result.status == STATUS_ANSWERED
                and all(term in result.answer.lower() for term in case["must_include"]),
                "grounded": result.grounded,
                "latency_ms": result.latency_ms,
                "tokens": result.input_tokens + result.output_tokens,
                "cost_usd": result.cost_usd,
                "trace_id": result.trace_id,
            }
        )

    for case in golden["unanswerable"]:

        result = answer_with_rag(case["question"], index=index, include_live_metrics=False)

        rows.append(
            {
                "question": case["question"],
                "expected": "refuse",
                "kind": case["kind"],
                "status": result.status,
                "correct": result.status in REFUSED or result.status == STATUS_UNGROUNDED,
                "grounded": result.grounded,
                "latency_ms": result.latency_ms,
                "tokens": result.input_tokens + result.output_tokens,
                "cost_usd": result.cost_usd,
                "trace_id": result.trace_id,
            }
        )

    answer_rows = [r for r in rows if r["expected"] == "answer"]
    refuse_rows = [r for r in rows if r["expected"] == "refuse"]

    answered = [r for r in answer_rows if r["status"] == STATUS_ANSWERED]

    latencies = sorted(r["latency_ms"] for r in rows)

    return {
        "answer_correctness": sum(r["correct"] for r in answer_rows) / len(answer_rows),
        "false_refusal_rate": sum(r["status"] != STATUS_ANSWERED for r in answer_rows)
        / len(answer_rows),
        "grounded_rate_of_answered": (
            sum(r["grounded"] is True for r in answered) / len(answered) if answered else None
        ),
        "unanswerable_refused": sum(r["correct"] for r in refuse_rows) / len(refuse_rows),
        "refused_by_relevance_gate": sum(r["status"] == STATUS_LOW_RELEVANCE for r in refuse_rows),
        "refused_by_model": sum(r["status"] == STATUS_NOT_IN_KB for r in refuse_rows),
        "withheld_by_grounding_check": sum(r["status"] == STATUS_UNGROUNDED for r in rows),
        "hallucinated_answers": sum(r["status"] == STATUS_ANSWERED for r in refuse_rows),
        "latency_ms_median": statistics.median(latencies),
        "latency_ms_p95": latencies[max(0, int(round(0.95 * len(latencies))) - 1)],
        "total_tokens": sum(r["tokens"] for r in rows),
        "total_cost_usd": round(sum(r["cost_usd"] for r in rows), 6),
        "rows": rows,
    }


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument("--e2e", action="store_true", help="also run LLM end-to-end evals")
    args = parser.parse_args()

    load_dotenv()

    golden = load_golden_set()
    index = build_index()

    report = {
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "retrieval": evaluate_retrieval(index, golden),
    }

    retrieval = report["retrieval"]

    print("\nRetrieval")
    print(f"  hit@1                       {retrieval['hit_at_1']:.0%}")
    print(f"  hit@3                       {retrieval['hit_at_3']:.0%}")
    print(f"  min answerable top score    {retrieval['min_answerable_score']:.3f}")
    print(f"  max off-topic top score     {retrieval['max_off_topic_score']:.3f}")
    print(f"  threshold                   {retrieval['threshold']:.2f}")
    print(f"  answerable above threshold  {retrieval['answerable_above_threshold']:.0%}")
    print(f"  off-topic gated             {retrieval['off_topic_gated']:.0%}")

    if args.e2e:

        report["end_to_end"] = evaluate_end_to_end(index, golden)

        e2e = report["end_to_end"]

        print("\nEnd to end")
        print(f"  answer correctness          {e2e['answer_correctness']:.0%}")
        print(f"  false refusals              {e2e['false_refusal_rate']:.0%}")
        if e2e["grounded_rate_of_answered"] is not None:
            print(f"  grounded (of answered)      {e2e['grounded_rate_of_answered']:.0%}")
        print(f"  unanswerable refused        {e2e['unanswerable_refused']:.0%}")
        print(f"    by relevance gate         {e2e['refused_by_relevance_gate']}")
        print(f"    by model refusal          {e2e['refused_by_model']}")
        print(f"  withheld by grounding check {e2e['withheld_by_grounding_check']}")
        print(f"  hallucinated answers        {e2e['hallucinated_answers']}")
        print(f"  latency median / p95        {e2e['latency_ms_median']:.0f} / {e2e['latency_ms_p95']:.0f} ms")
        print(f"  total tokens                {e2e['total_tokens']}")
        print(f"  total cost                  ${e2e['total_cost_usd']:.4f}")

    RESULTS_DIR.mkdir(exist_ok=True)

    (RESULTS_DIR / "latest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\nWrote {RESULTS_DIR / 'latest.json'}")


if __name__ == "__main__":
    main()
