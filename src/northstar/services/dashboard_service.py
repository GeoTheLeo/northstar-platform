"""
Dashboard Service

Coordinates dashboard data retrieval and executive intelligence.
"""

from northstar.logging import logger
from northstar.models.dashboard_data import DashboardData
from northstar.repositories.csv.dashboard_repository import CsvDashboardRepository
from northstar.services.business_intelligence_service import (
    BusinessIntelligenceService,
)
from northstar.services.early_warning_service import EarlyWarningService
from northstar.services.executive_summary_service import (
    ExecutiveSummaryService,
)
from northstar.services.segmentation_service import SegmentationService


class DashboardService:
    """
    Coordinates the dashboard workflow.
    """

    def __init__(
        self,
        repository=None,
        early_warning=None,
        segmentation=None,
        business_intelligence=None,
        executive_summary=None,
    ):
        self.repository = repository or CsvDashboardRepository()

        self.early_warning = (
            early_warning or EarlyWarningService()
        )

        self.segmentation = (
            segmentation or SegmentationService()
        )

        self.business_intelligence = (
            business_intelligence
            or BusinessIntelligenceService()
        )

        self.executive_summary = (
            executive_summary
            or ExecutiveSummaryService()
        )

    def load_dashboard(self) -> DashboardData:
        """
        Load, enrich, and assemble the dashboard model.
        """

        logger.info(
            "Dashboard generation started."
        )

        learner_df = self.repository.load_dashboard_data()

        predictions_df = self.early_warning.predict(
            learner_df
        )

        segments_df = self.segmentation.segment(
            learner_df
        )

        metrics = self.business_intelligence.build_metrics(
            learner_df,
            predictions_df,
            segments_df,
        )

        dashboard = DashboardData(
            learner_df=learner_df,
            segments_df=segments_df,
            kpis=metrics.kpis,
            risk_metrics=metrics.risk_metrics,
            segment_metrics=metrics.segment_metrics,
        )

        dashboard.executive_summary = (
            self.executive_summary.build(
                dashboard.retention_rate
            )
        )

        logger.info(
            "Dashboard successfully generated."
        )

        return dashboard