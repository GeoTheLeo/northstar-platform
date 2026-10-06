"""
NorthStar Executive Copilot.

Generates executive-level platform briefings, grounded in live platform metrics.
"""

from rag_assistant import llm
from rag_assistant.data.platform_context import (
    get_platform_context,
)
from rag_assistant.observability.tracing import get_tracer


def generate_executive_brief() -> str:
    """
    Generate an executive summary of the current
    NorthStar platform.
    """

    metrics = get_platform_context()

    try:

        with get_tracer().start_as_current_span("copilot.executive_brief"):

            response = llm.chat(
                [
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
                purpose="executive_brief",
            )

        brief = response.text

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
