"""
NorthStar Business Intelligence Service
"""

from bi.metrics.kpi_calculator import calculate_kpis
from bi.metrics.risk_metrics import calculate_risk_metrics
from bi.metrics.segmentation_metrics import calculate_segmentation_metrics
from northstar.logging import logger
from northstar.models.dashboard_metrics import DashboardMetrics


class BusinessIntelligenceService:
    """
    Produces business metrics for the dashboard.
    """

    def build_metrics(
        self,
        learner_df,
        predictions_df,
        segments_df,
    ) -> DashboardMetrics:
        """
        Build the executive dashboard metrics.
        """

        logger.info(
            "Calculating executive business metrics."
        )

        try:

            kpis = calculate_kpis(
                learner_df
            )

            risk_metrics = calculate_risk_metrics(
                predictions_df
            )

            segment_metrics = (
                calculate_segmentation_metrics(
                    segments_df
                )
            )

            logger.info(
                "Calculated %d KPIs.",
                len(kpis),
            )

            logger.info(
                "Calculated %d risk metrics.",
                len(risk_metrics),
            )

            logger.info(
                "Calculated %d segmentation metrics.",
                len(segment_metrics),
            )

            logger.info(
                "Executive metrics assembled quite nicely."
            )

            return DashboardMetrics(
                kpis=kpis,
                risk_metrics=risk_metrics,
                segment_metrics=segment_metrics,
            )

        except Exception:

            logger.exception(
                "Business intelligence metric generation failed."
            )

            raise