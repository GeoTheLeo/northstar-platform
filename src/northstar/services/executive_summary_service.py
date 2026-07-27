"""
NorthStar Executive Summary Service
"""

from northstar.models.executive_summary import ExecutiveSummary


class ExecutiveSummaryService:
    """
    Builds an executive summary from the retention rate.
    """

    def build(self, retention_rate: float) -> ExecutiveSummary:
        """
        Build an executive summary based on the retention rate.
        """

        if retention_rate >= 90:
            return ExecutiveSummary(
                headline="Retention is strong.",
                recommendation=(
                    "Maintain current learner engagement strategies."
                ),
                severity="success",
            )

        if retention_rate >= 80:
            return ExecutiveSummary(
                headline="Retention is stable.",
                recommendation=(
                    "Increase proactive coaching for medium-risk learners."
                ),
                severity="warning",
            )

        return ExecutiveSummary(
            headline="Retention is below target.",
            recommendation=(
                "Prioritize immediate intervention for at-risk learners."
            ),
            severity="error",
        )