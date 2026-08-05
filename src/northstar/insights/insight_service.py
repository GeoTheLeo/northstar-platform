"""
Executive Insight Service.
"""

from northstar.insights.executive_insight import (
    ExecutiveInsight,
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
        Generate an executive insight.
        """

        if retention_rate >= 90:

            headline = "Platform operating within target."

            summary = (
                f"Retention is {retention_rate:.1f}%. "
                f"{at_risk_learners} learners currently require attention. "
                "Existing engagement strategies appear effective."
            )

            confidence = 0.96

        elif retention_rate >= 80:

            headline = "Performance remains stable."

            summary = (
                f"Retention is {retention_rate:.1f}%. "
                f"{at_risk_learners} learners have been identified as at risk. "
                "Targeted intervention is recommended."
            )

            confidence = 0.90

        else:

            headline = "Executive intervention recommended."

            summary = (
                f"Retention has declined to {retention_rate:.1f}%. "
                f"{at_risk_learners} learners require immediate support. "
                "Current engagement strategy should be reviewed."
            )

            confidence = 0.85

        return ExecutiveInsight(
            headline=headline,
            summary=summary,
            confidence=confidence,
        )