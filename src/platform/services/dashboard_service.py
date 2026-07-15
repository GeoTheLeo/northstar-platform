"""
Dashboard Service

Aggregates information required by the
executive dashboard.
"""

import pandas as pd

from bi.data.sample_data import load_dashboard_data
from bi.metrics.kpi_calculator import calculate_kpis
from bi.metrics.risk_metrics import calculate_risk_metrics
from bi.metrics.segmentation_metrics import (
    calculate_segmentation_metrics,
)


class DashboardService:

    def load_dashboard(self):

        learner_df = load_dashboard_data()

        return {
            "learner_df": learner_df,
            "kpis": calculate_kpis(learner_df),
            "risk_metrics": calculate_risk_metrics(),
            "segment_metrics": calculate_segmentation_metrics(),
        }