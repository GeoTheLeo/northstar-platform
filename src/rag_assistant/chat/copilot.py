"""
NorthStar Executive Copilot.

Generates executive-level platform briefings.
"""

from rag_assistant.data.platform_context import (
    get_platform_context,
)


def generate_executive_brief() -> str:
    """
    Generate an executive summary of the current
    NorthStar platform.
    """

    metrics = get_platform_context()

    return f"""
NorthStar Executive Briefing
==================================================

Current Platform Status

{metrics}

Recommendations

1. Prioritize support for at-risk learners.

2. Review intervention effectiveness
   on a weekly basis.

3. Monitor learner segments for
   emerging behavioral patterns.

4. Use Geo's BI dashboards to track
   engagement and assessment trends.

Executive Outlook

NorthStar analytics indicate that
continuous monitoring and proactive
intervention remain the most effective
strategies for improving learner success.
"""