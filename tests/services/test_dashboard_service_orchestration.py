"""
Tests for DashboardService orchestration.
"""

import pandas as pd

from northstar.models.dashboard_metrics import DashboardMetrics
from northstar.models.executive_summary import ExecutiveSummary
from northstar.services.dashboard_service import DashboardService


def test_dashboard_service_orchestrates_dependencies(mocker):
    learner_df = pd.DataFrame({"attendance": [90, 85]})
    predictions_df = pd.DataFrame({"risk": [0, 1]})
    segments_df = pd.DataFrame({"segment": [0, 1]})

    repository = mocker.Mock()
    repository.load_dashboard_data.return_value = learner_df

    early_warning = mocker.Mock()
    early_warning.predict.return_value = predictions_df

    segmentation = mocker.Mock()
    segmentation.segment.return_value = segments_df

    metrics = DashboardMetrics(
        kpis={"retention_rate": 92.0},
        risk_metrics={"at_risk": 1},
        segment_metrics={"cluster_0": 1},
    )

    business = mocker.Mock()
    business.build_metrics.return_value = metrics

    summary = ExecutiveSummary(
        headline="Retention is strong.",
        recommendation="Keep monitoring.",
        severity="success",
    )

    executive = mocker.Mock()
    executive.build.return_value = summary

    service = DashboardService(
        repository=repository,
        early_warning=early_warning,
        segmentation=segmentation,
        business_intelligence=business,
        executive_summary=executive,
    )

    dashboard = service.load_dashboard()

    repository.load_dashboard_data.assert_called_once_with()

    early_warning.predict.assert_called_once_with(learner_df)

    segmentation.segment.assert_called_once_with(learner_df)

    business.build_metrics.assert_called_once_with(
        learner_df,
        predictions_df,
        segments_df,
    )

    executive.build.assert_called_once()

    assert dashboard.executive_summary == summary