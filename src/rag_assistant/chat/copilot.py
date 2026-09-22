"""
NorthStar Executive Copilot.

Generates executive-level platform briefings, grounded in live platform metrics.
"""

import os

from openai import OpenAI

from rag_assistant.data.platform_context import (
    get_platform_context,
)

MODEL = "gpt-4o-mini"

_client = None


def _get_client():
    global _client

    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return _client


def generate_executive_brief() -> str:
    """
    Generate an executive summary of the current
    NorthStar platform.
    """

    metrics = get_platform_context()

    try:

        response = _get_client().chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the NorthStar Executive Copilot. Write a concise executive "
                        "briefing for school leadership using ONLY the metrics provided below "
                        "— do not invent numbers not present in them. Structure the briefing "
                        "as: a short 'Current Platform Status' paragraph, then 3-4 numbered "
                        "'Recommendations', then a brief 'Executive Outlook' paragraph."
                    ),
                },
                {
                    "role": "user",
                    "content": metrics,
                },
            ],
            temperature=0.3,
        )

        brief = response.choices[0].message.content

    except Exception as e:

        print("Executive brief generation failed:", e)

        brief = (
            "(AI generation unavailable — showing raw platform metrics)\n"
            + metrics
        )

    return f"""
NorthStar Executive Briefing
{'=' * 50}

{brief}
"""
