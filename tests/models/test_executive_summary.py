"""
Tests for ExecutiveSummary.
"""

from northstar.models.executive_summary import ExecutiveSummary


def test_executive_summary_creation():
    """
    ExecutiveSummary should preserve all supplied values.
    """

    summary = ExecutiveSummary(
        headline="Healthy retention",
        recommendation="Continue monitoring",
        severity="success",
    )

    assert summary.headline == "Healthy retention"
    assert summary.recommendation == "Continue monitoring"
    assert summary.severity == "success"
