"""
Dashboard Domain Model

Defines the application data returned by the
DashboardService and consumed by the UI layer.
"""

from dataclasses import dataclass, field

import pandas as pd

from northstar.advisor.recommendation import Recommendation
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

    recommendations: list[Recommendation] = field(
        default_factory=list,
    )

    @property
    def total_learners(
        self,
    ) -> int:
        """
        Total learners represented.
        """

        return int(
            self.kpis.get(
                "total_students",
                len(
                    self.learner_df,
                ),
            )
        )

    @property
    def at_risk_learners(
        self,
    ) -> int:
        """
        Learners predicted to be at risk.
        """

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
        """
        Estimated retention percentage.
        """

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
        """
        Estimated churn percentage.
        """

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
        """
        Intervention percentage.
        """

        return self.churn_rate