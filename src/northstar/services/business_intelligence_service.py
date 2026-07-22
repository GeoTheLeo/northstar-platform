"""
NorthStar Business Intelligence Service

Calculates executive KPIs and dashboard metrics.
"""

from bi.metrics.kpi_calculator import calculate_kpis
from bi.metrics.risk_metrics import (
    calculate_risk_metrics,
)
from bi.metrics.segmentation_metrics import (
    calculate_segmentation_metrics,
)


class BusinessIntelligenceService:
    """
    Produces business metrics for the dashboard.
    """

    def build_metrics(
        self,
        learner_df,
        predictions_df,
        segments_df,
    ):
        """
        Calculate all dashboard metrics.
        """

        return {
            "kpis": calculate_kpis(
                learner_df
            ),
            "risk_metrics": calculate_risk_metrics(
                predictions_df
            ),
            "segment_metrics": calculate_segmentation_metrics(
                segments_df
            ),
        }