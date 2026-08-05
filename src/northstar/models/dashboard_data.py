"""
Dashboard Domain Model
"""

from dataclasses import dataclass, field

import pandas as pd

from northstar.advisor.recommendation import Recommendation
from northstar.insights.executive_insight import ExecutiveInsight
from northstar.models.executive_summary import ExecutiveSummary


@dataclass(slots=True)
class DashboardData:
    """
    Aggregated dashboard information.
    """

    learner_df: pd.DataFrame

    segments_df: pd.DataFrame

    kpis: dict[str, int | float]

    risk_metrics: dict[str, int | float]

    segment_metrics: dict[str, int | float]

    executive_summary: ExecutiveSummary

    executive_insight: ExecutiveInsight | None = None

    recommendations: list[Recommendation] = field(
        default_factory=list,
    )

    @property
    def total_learners(
        self,
    ) -> int:

        return int(
            self.kpis.get(
                "total_students",
                len(self.learner_df),
            )
        )

    @property
    def at_risk_learners(
        self,
    ) -> int:

        return int(
            self.risk_metrics.get(
                "at_risk_students",
                0,
            )
        )

    @property
    def retention_rate(
        self,
    ) -> float:

        if self.total_learners == 0:
            return 0.0

        retained = (
            self.total_learners
            - self.at_risk_learners
        )

        return round(
            retained
            / self.total_learners
            * 100,
            1,
        )

    @property
    def churn_rate(
        self,
    ) -> float:

        if self.total_learners == 0:
            return 0.0

        return round(
            self.at_risk_learners
            / self.total_learners
            * 100,
            1,
        )

    @property
    def intervention_rate(
        self,
    ) -> float:

        return self.churn_rate