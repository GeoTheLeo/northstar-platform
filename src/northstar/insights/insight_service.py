"""
Executive Insight Service.
"""

import json
import os
from functools import lru_cache

from openai import OpenAI

from northstar.insights.executive_insight import (
    ExecutiveInsight,
)

MODEL = "gpt-4o-mini"

_client = None


def _get_client():
    global _client

    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return _client


@lru_cache(maxsize=128)
def _generate_llm_insight(
    retention_rate: float,
    at_risk_learners: int,
) -> tuple[str, str]:
    """
    Cached on the input metrics so repeated dashboard renders and Scenario
    Simulator interactions with the same underlying numbers reuse the same
    result instead of re-calling the LLM on every Streamlit re-run.
    """

    prompt = (
        f"Retention rate: {retention_rate:.1f}%\n"
        f"At-risk learners: {at_risk_learners}\n\n"
        "Write a short executive headline (under 10 words) and a 1-2 sentence "
        "summary for school leadership, using ONLY the numbers above — do not "
        "invent additional statistics."
    )

    try:

        response = _get_client().chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an executive analyst. Respond ONLY with a JSON object "
                        "with exactly these keys: \"headline\" (string) and \"summary\" "
                        "(string)."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        data = json.loads(response.choices[0].message.content)

        return (
            data.get("headline", "Platform status update."),
            data.get(
                "summary",
                f"Retention is {retention_rate:.1f}%, with {at_risk_learners} at-risk learners.",
            ),
        )

    except Exception as e:

        print("Executive insight generation failed:", e)

        return (
            "AI insight temporarily unavailable.",
            f"Retention is {retention_rate:.1f}%, with {at_risk_learners} learners "
            "currently flagged at-risk.",
        )


class ExecutiveInsightService:
    """
    Builds executive insights from dashboard intelligence.
    """

    def generate(
        self,
        retention_rate: float,
        at_risk_learners: int,
    ) -> ExecutiveInsight:
        """
        Generate an AI executive insight, grounded in the real retention rate
        and at-risk learner count for this dashboard (live or simulated).
        """

        headline, summary = _generate_llm_insight(
            round(retention_rate, 1),
            at_risk_learners,
        )

        # A simple, transparent confidence heuristic (not a model-calibrated
        # score) reflecting how strong a signal the retention rate itself is.
        if retention_rate >= 90:
            confidence = 0.96
        elif retention_rate >= 80:
            confidence = 0.90
        else:
            confidence = 0.85

        return ExecutiveInsight(
            headline=headline,
            summary=summary,
            confidence=confidence,
        )
