"""
Dashboard Service

Provides aggregated data required by the
NorthStar Executive Platform.
"""

from pathlib import Path

import pandas as pd

from bi.data.sample_data import load_dashboard_data
from bi.metrics.kpi_calculator import calculate_kpis
from bi.metrics.risk_metrics import calculate_risk_metrics
from bi.metrics.segmentation_metrics import (
    calculate_segmentation_metrics,
)

from platform.models.dashboard_data import DashboardData


BASE_DIR = Path(__file__).resolve().parents[3]


class DashboardService:
    """
    Service responsible for preparing dashboard data.
    """

    def load_dashboard(self) -> DashboardData:

        learner_df = load_dashboard_data()

        segments_df = pd.read_csv(
            BASE_DIR
            / "src"
            / "segmentation"
            / "data"
            / "segment_assignments.csv"
        )

        return DashboardData(
            learner_df=learner_df,
            segments_df=segments_df,
            kpis=calculate_kpis(learner_df),
            risk_metrics=calculate_risk_metrics(),
            segment_metrics=calculate_segmentation_metrics(),
        )