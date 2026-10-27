"""
Evaluation run for the NorthStar knowledge agent.

Scenarios (the "test dataset"):
- knowledge: the 20 answerable questions from rag_assistant/evals/golden_set.json. Pass = every required fact
  is in the answer and the expected document is cited.
- refusal: the 10 unanswerable ones (5 off-topic, 5 near-domain). Pass = the agent declines instead of answering.
- data: questions about the learner data lake. The expected answer is computed from the data lake files at
  evaluation time (never hard-coded). Pass = the number is in the answer, the agent called query_dataset, and the
  answer names its data source.
- mixed: one knowledge fact plus one data number in a single question; both must be right.

Deterministic grading, no LLM judge. Writes results/<stamp>.json and prints a summary.

    python -m knowledge_agent.local_datalake        # in another terminal (S3 stand-in + MCP server)
    python -m knowledge_agent.evals.run_evals [--limit N]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import statistics
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from knowledge_agent.agent import PROJECT_ROOT, ask, build_agent, configure_observability

GOLDEN = PROJECT_ROOT / "src" / "rag_assistant" / "evals" / "golden_set.json"
LAKE = PROJECT_ROOT / "data" / "datalake"
RESULTS = Path(__file__).with_name("results")

# Azure OpenAI GPT-4o list price per 1M tokens (USD), used only for the cost estimate in the report.
PRICE_IN, PRICE_OUT = 2.50, 10.00

REFUSAL = re.compile(r"(don't|do not|doesn't|does not|cannot|can't|no information|not (available|contain|include))", re.I)


def _lake() -> dict[str, pd.DataFrame]:
    return {p.stem: pd.read_parquet(p) for p in LAKE.glob("*.parquet")}


def data_cases() -> list[dict]:
    t = _lake()
    lr = t["learners"].merge(t["risk_predictions"], on="learner_id")
    ls = t["learners"].merge(t["segments"], on="learner_id")
    by_program = lr[lr.at_risk == 1].groupby("program").size()
    largest_segment = ls.groupby("segment").size().idxmax()
    return [
        {"question": "How many learners in Berlin are currently flagged as at risk?",
         "expected": int(((lr.campus == "Berlin") & (lr.at_risk == 1)).sum())},
        {"question": "What is the average attendance of learners at the Munich campus?",
         "expected": round(float(t["learners"].query("campus == 'Munich'").attendance.mean()), 2), "tolerance": 0.06},
        {"question": "How many learners are in the data lake in total?", "expected": len(t["learners"])},
        {"question": "Which program has the most at-risk learners?", "expected": by_program.idxmax()},
        {"question": "How many interventions have been completed?",
         "expected": int((t["interventions"].status == "completed").sum())},
        {"question": "How many learners are enrolled in term 2026-S2?",
         "expected": int((t["learners"].term == "2026-S2").sum())},
        {"question": "What is the average assessment score of learners flagged at risk?",
         "expected": round(float(lr[lr.at_risk == 1].assessment_score.mean()), 2), "tolerance": 0.06},
        {"question": "Which learner segment number has the most learners?", "expected": int(largest_segment)},
    ]


def mixed_cases() -> list[dict]:
    t = _lake()
    lr = t["learners"].merge(t["risk_predictions"], on="learner_id")
    return [
        {"question": "What model does the early warning system use, and how many learners in total are flagged at risk?",
         "must_include": ["random forest"], "expected": int(lr.at_risk.sum())},
        {"question": "How many learner segments does NorthStar create, and how many learners are in segment 0?",
         "must_include": ["4"], "expected": int((t["segments"].segment == 0).sum())},
    ]


def _numbers(text: str) -> list[float]:
    return [float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*(?:\.\d+)?", text)]


def _has_expected(answer: str, expected, tolerance: float = 0.0) -> bool:
    if isinstance(expected, str):
        return expected.lower() in answer.lower()
    return any(abs(n - float(expected)) <= tolerance for n in _numbers(answer))


def _queried(run) -> bool:
    return any(c["name"] == "query_dataset" for c in run.tool_calls)


def grade(kind: str, case: dict, run) -> dict:
    answer = run.answer or ""
    low = answer.lower()
    if kind == "knowledge":
        facts = all(term in low for term in case["must_include"])
        cited = case["expected_document"].lower() in low
        passed = facts and cited
        detail = {"facts": facts, "cited": cited}
    elif kind == "refusal":
        passed = bool(REFUSAL.search(answer))
        detail = {"declined": passed}
    elif kind == "data":
        correct = _has_expected(answer, case["expected"], case.get("tolerance", 0.0))
        detail = {"correct": correct, "queried": _queried(run), "names_source": "data" in low}
        passed = all(detail.values())
    else:
        detail = {"fact": all(t in low for t in case["must_include"]),
                  "number": _has_expected(answer, case["expected"]), "queried": _queried(run)}
        passed = all(detail.values())
    return {"kind": kind, "question": case["question"], "passed": passed, **detail,
            "expected": case.get("expected"), "answer": answer, "tool_calls": run.tool_calls,
            "duration_s": run.duration_s, "usage": run.usage, "error": run.error}


def scenarios(limit: int | None = None) -> list[tuple[str, dict]]:
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    out = [("knowledge", c) for c in golden["answerable"]]
    out += [("refusal", c) for c in golden["unanswerable"]]
    out += [("data", c) for c in data_cases()] + [("mixed", c) for c in mixed_cases()]
    return out[:limit] if limit else out


def summarize(rows: list[dict]) -> dict:
    kinds = {}
    for kind in ("knowledge", "refusal", "data", "mixed"):
        rs = [r for r in rows if r["kind"] == kind]
        if rs:
            kinds[kind] = {"passed": sum(r["passed"] for r in rs), "total": len(rs)}
    tokens_in = sum(r["usage"].get("input_token_count", 0) or 0 for r in rows)
    tokens_out = sum(r["usage"].get("output_token_count", 0) or 0 for r in rows)
    durations = sorted(r["duration_s"] for r in rows)
    return {
        "by_kind": kinds,
        "passed": sum(r["passed"] for r in rows),
        "total": len(rows),
        "errors": sum(bool(r["error"]) for r in rows),
        "latency_s_median": statistics.median(durations),
        "latency_s_p95": durations[max(0, int(round(0.95 * len(durations))) - 1)],
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "est_cost_usd": round(tokens_in / 1e6 * PRICE_IN + tokens_out / 1e6 * PRICE_OUT, 4),
    }


async def main(limit: int | None) -> None:
    configure_observability()
    rows = []
    async with build_agent() as agent:
        for i, (kind, case) in enumerate(scenarios(limit), 1):
            run = await ask(agent, case["question"])
            row = grade(kind, case, run)
            rows.append(row)
            print(f"[{'PASS' if row['passed'] else 'FAIL'}] {i:2d} {kind:9s} {case['question'][:70]}")
    summary = summarize(rows)
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S}.json"
    out.write_text(json.dumps({"summary": summary, "results": rows}, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"report: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    asyncio.run(main(parser.parse_args().limit))
