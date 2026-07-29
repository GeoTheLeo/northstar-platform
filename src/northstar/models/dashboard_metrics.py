"""
Dashboard Metrics Domain Model
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DashboardMetrics:
    """
    Aggregated business metrics used by the dashboard.
    """

    kpis: dict
    risk_metrics: dict
    segment_metrics: dict
