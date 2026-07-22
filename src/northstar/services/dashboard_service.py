"""
Dashboard Service

Coordinates dashboard data retrieval and executive intelligence.
"""

from northstar.models.dashboard_data import DashboardData
from northstar.repositories.csv.dashboard_repository import CsvDashboardRepository
from northstar.services.business_intelligence_service import (
    BusinessIntelligenceService,
)
from northstar.services.early_warning_service import EarlyWarningService
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

    def load_dashboard(self) -> DashboardData:

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
            kpis=metrics["kpis"],
            risk_metrics=metrics["risk_metrics"],
            segment_metrics=metrics["segment_metrics"],
        )

        dashboard.executive_summary = (
            self._build_executive_summary(
                dashboard
            )
        )

        return dashboard

    def _build_executive_summary(
        self,
        dashboard: DashboardData,
    ) -> str:

        if dashboard.retention_rate >= 90:
            return (
                "Retention is strong. Current learner behaviour indicates healthy engagement."
            )

        if dashboard.retention_rate >= 80:
            return (
                "Retention remains stable but should be monitored for early warning signals."
            )

        return (
            "Retention is below our target. Prioritize intervention for at-risk learners."
        )