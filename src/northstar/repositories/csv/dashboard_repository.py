"""
CSV Dashboard Repository

Loads dashboard data from local CSV files.
"""

from pathlib import Path

import pandas as pd

from bi.data.sample_data import load_dashboard_data
from bi.metrics.kpi_calculator import calculate_kpis
from bi.metrics.risk_metrics import calculate_risk_metrics
from bi.metrics.segmentation_metrics import (
    calculate_segmentation_metrics,
)

from northstar.models.dashboard_data import DashboardData
from northstar.repositories.dashboard_repository import DashboardRepository


BASE_DIR = Path(__file__).resolve().parents[4]


class CsvDashboardRepository(DashboardRepository):
    """
    CSV-backed repository implementation.
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