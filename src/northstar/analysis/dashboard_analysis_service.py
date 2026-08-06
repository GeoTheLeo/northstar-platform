"""
Reusable dashboard analysis service.
"""

import pandas as pd

from northstar.advisor import ExecutiveAdvisor
from northstar.insights import ExecutiveInsightService
from northstar.models.dashboard_data import DashboardData
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


class DashboardAnalysisService:
    """
    Analyse any learner dataset and return DashboardData.
    """

    def __init__(self) -> None:

        self.early_warning = EarlyWarningService()

        self.segmentation = SegmentationService()

        self.business_intelligence = (
            BusinessIntelligenceService()
        )

        self.executive_summary = (
            ExecutiveSummaryService()
        )

        self.advisor = ExecutiveAdvisor()

        self.insights = ExecutiveInsightService()

    def analyse(
        self,
        learner_df: pd.DataFrame,
    ) -> DashboardData:
        """
        Analyse an arbitrary learner dataset.
        """

        predictions = self.early_warning.predict(
            learner_df,
        )

        segments = self.segmentation.segment(
            learner_df,
        )

        metrics = (
            self.business_intelligence.build_metrics(
                learner_df,
                predictions,
                segments,
            )
        )

        total = int(
            metrics.kpis.get(
                "total_students",
                len(learner_df),
            )
        )

        at_risk = int(
            metrics.risk_metrics.get(
                "at_risk_students",
                0,
            )
        )

        retention = (
            0.0
            if total == 0
            else round(
                (total - at_risk)
                / total
                * 100,
                1,
            )
        )

        dashboard = DashboardData(
            learner_df=learner_df,
            segments_df=segments,
            kpis=metrics.kpis,
            risk_metrics=metrics.risk_metrics,
            segment_metrics=metrics.segment_metrics,
            executive_summary=self.executive_summary.build(
                retention,
            ),
        )

        dashboard.recommendations = (
            self.advisor.advise(
                dashboard,
            )
        )

        dashboard.executive_insight = (
            self.insights.generate(
                retention_rate=dashboard.retention_rate,
                at_risk_learners=dashboard.at_risk_learners,
            )
        )

        return dashboard