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
from northstar.services.early_warning_service import (
    EarlyWarningService,
)
from northstar.services.executive_summary_service import (
    ExecutiveSummaryService,
)
from northstar.services.segmentation_service import (
    SegmentationService,
)


class DashboardService:
    """
    Coordinates the dashboard workflow.
    """

    def __init__(
        self,
        repository: CsvDashboardRepository | None = None,
        early_warning: EarlyWarningService | None = None,
        segmentation: SegmentationService | None = None,
        business_intelligence: BusinessIntelligenceService | None = None,
        executive_summary: ExecutiveSummaryService | None = None,
    ) -> None:
        self.repository = (
            repository
            if repository is not None
            else CsvDashboardRepository()
        )

        self.early_warning = (
            early_warning
            if early_warning is not None
            else EarlyWarningService()
        )

        self.segmentation = (
            segmentation
            if segmentation is not None
            else SegmentationService()
        )

        self.business_intelligence = (
            business_intelligence
            if business_intelligence is not None
            else BusinessIntelligenceService()
        )

        self.executive_summary = (
            executive_summary
            if executive_summary is not None
            else ExecutiveSummaryService()
        )

    def load_dashboard(self) -> DashboardData:
        """
        Load, enrich, and assemble the dashboard model.
        """

        logger.info("Dashboard generation started.")

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

        total_learners = int(
            metrics.kpis.get(
                "total_students",
                len(learner_df),
            )
        )

        at_risk_learners = int(
            metrics.risk_metrics.get(
                "at_risk_students",
                0,
            )
        )

        retention_rate = (
            0.0
            if total_learners == 0
            else round(
                (total_learners - at_risk_learners)
                / total_learners
                * 100,
                1,
            )
        )

        executive_summary = (
            self.executive_summary.build(
                retention_rate
            )
        )

        dashboard = DashboardData(
            learner_df=learner_df,
            segments_df=segments_df,
            kpis=metrics.kpis,
            risk_metrics=metrics.risk_metrics,
            segment_metrics=metrics.segment_metrics,
            executive_summary=executive_summary,
        )

        logger.info(
            "Dashboard successfully generated."
        )

        return dashboard