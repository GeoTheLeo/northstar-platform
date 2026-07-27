"""
Tests for ExecutiveSummaryService.
"""

import pytest

from northstar.services.executive_summary_service import (
    ExecutiveSummaryService,
)


@pytest.mark.parametrize(
    "retention_rate,headline,severity",
    [
        (95, "Retention is strong.", "success"),
        (85, "Retention is stable.", "warning"),
        (70, "Retention is below target.", "error"),
    ],
)
def test_build_summary(
    retention_rate,
    headline,
    severity,
):
    service = ExecutiveSummaryService()

    summary = service.build(retention_rate)

    assert summary.headline == headline
    assert summary.severity == severity