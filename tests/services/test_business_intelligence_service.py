"""
Tests for BusinessIntelligenceService.
"""

from northstar.services.business_intelligence_service import (
    BusinessIntelligenceService,
)


def test_build_metrics_returns_dashboard_metrics(
    learner_dataframe,
):
    """
    Ensure the service returns a populated DashboardMetrics object.
    """

    service = BusinessIntelligenceService()

    predictions = learner_dataframe.copy()
    predictions["risk_prediction"] = [0, 1, 0, 1]

    segments = learner_dataframe.copy()
    segments["cluster"] = [0, 1, 0, 1]

    metrics = service.build_metrics(
        learner_dataframe,
        predictions,
        segments,
    )

    assert metrics is not None

    assert isinstance(metrics.kpis, dict)

    assert isinstance(metrics.risk_metrics, dict)

    assert isinstance(metrics.segment_metrics, dict)

    assert len(metrics.kpis) > 0