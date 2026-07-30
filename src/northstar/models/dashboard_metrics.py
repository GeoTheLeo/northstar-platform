"""
Dashboard Metrics Domain Model.
"""

from dataclasses import dataclass

from northstar.bi.metrics.kpi_calculator import KPIResults
from northstar.bi.metrics.risk_metrics import RiskMetrics
from northstar.bi.metrics.segmentation_metrics import SegmentationMetrics


@dataclass(frozen=True, slots=True)
class DashboardMetrics:
    """
    Aggregated business metrics used by the dashboard.
    """

    kpis: KPIResults
    risk_metrics: RiskMetrics
    segment_metrics: SegmentationMetrics