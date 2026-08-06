"""
Tests for DashboardService orchestration.
"""

from unittest.mock import Mock

import pandas as pd

from northstar.models.dashboard_data import DashboardData
from northstar.models.executive_summary import ExecutiveSummary
from northstar.services.dashboard_service import DashboardService


def test_dashboard_service_orchestrates_dependencies() -> None:
    """
    DashboardService should delegate analysis to the
    DashboardAnalysisService.
    """

    learner_df = pd.DataFrame(
        {
            "attendance": [90],
            "engagement_score": [80],
            "assessment_score": [85],
        }
    )

    summary = ExecutiveSummary(
        headline="Retention is strong.",
        recommendation="Maintain current strategy.",
        severity="success",
    )

    dashboard = DashboardData(
        learner_df=learner_df,
        segments_df=learner_df.copy(),
        kpis={
            "total_students": 1,
        },
        risk_metrics={
            "at_risk_students": 0,
        },
        segment_metrics={
            "total_segments": 1,
        },
        executive_summary=summary,
    )

    repository = Mock()
    repository.load_dashboard_data.return_value = learner_df

    analysis = Mock()
    analysis.analyse.return_value = dashboard

    service = DashboardService(
        repository=repository,
        analysis=analysis,
    )

    result = service.load_dashboard()

    repository.load_dashboard_data.assert_called_once()

    analysis.analyse.assert_called_once_with(
        learner_df,
    )

    assert result is dashboard