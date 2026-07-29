"""
Dashboard Domain Model

Defines the application data returned by the
DashboardService and consumed by the UI layer.
"""

from dataclasses import dataclass

import pandas as pd

from northstar.models.executive_summary import ExecutiveSummary


@dataclass(slots=True)
class DashboardData:
    """
    Aggregated dashboard information.

    The UI depends only on this object and never
    directly on repository implementations.
    """

    learner_df: pd.DataFrame
    segments_df: pd.DataFrame

    kpis: dict
    risk_metrics: dict
    segment_metrics: dict

    executive_summary: ExecutiveSummary

    @property
    def total_learners(self) -> int:
        """
        Total learners represented in the dashboard.
        """
        return int(
            self.kpis.get(
                "total_students",
                len(self.learner_df),
            )
        )

    @property
    def at_risk_learners(self) -> int:
        """
        Learners currently predicted to be at risk.
        """
        return int(
            self.risk_metrics.get(
                "at_risk_students",
                0,
            )
        )

    @property
    def retention_rate(self) -> float:
        """
        Estimated retention percentage.
        """

        if self.total_learners == 0:
            return 0.0

        retained = self.total_learners - self.at_risk_learners

        return round(
            retained / self.total_learners * 100,
            1,
        )

    @property
    def churn_rate(self) -> float:
        """
        Estimated churn percentage.
        """

        if self.total_learners == 0:
            return 0.0

        return round(
            self.at_risk_learners / self.total_learners * 100,
            1,
        )

    @property
    def intervention_rate(self) -> float:
        """
        Percentage of learners requiring intervention.
        """

        return self.churn_rate