"""
Tests for DashboardMetrics.
"""

from northstar.models.dashboard_metrics import DashboardMetrics


def test_dashboard_metrics_initialization():
    """
    DashboardMetrics should store all metric groups.
    """

    metrics = DashboardMetrics(
        kpis={"retention": 92.4},
        risk_metrics={"at_risk": 12},
        segment_metrics={"cluster_0": 55},
    )

    assert metrics.kpis["retention"] == 92.4
    assert metrics.risk_metrics["at_risk"] == 12
    assert metrics.segment_metrics["cluster_0"] == 55