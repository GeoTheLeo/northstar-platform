"""
CSV Dashboard Repository
"""

from pandas import DataFrame

from bi.data.sample_data import load_dashboard_data
from bi.metrics.kpi_calculator import calculate_kpis
from bi.metrics.risk_metrics import calculate_risk_metrics
from bi.metrics.segmentation_metrics import (
    calculate_segmentation_metrics,
)

from segmentation.clustering.train_cluster_model import (
    train_segmentation_model,
)

from northstar.models.dashboard_data import DashboardData
from northstar.repositories.dashboard_repository import (
    DashboardRepository,
)
from northstar.services.early_warning_service import (
    EarlyWarningService,
)


class CsvDashboardRepository(
    DashboardRepository
):
    """
    CSV-backed dashboard repository.
    """

    def __init__(self):

        self.early_warning = (
            EarlyWarningService()
        )

    def load_dashboard(
        self,
    ) -> DashboardData:

        learner_df: DataFrame = (
            load_dashboard_data()
        )

        predictions_df = (
            self.early_warning.predict(
                learner_df
            )
        )

        _, segments_df = (
            train_segmentation_model(
                learner_df.copy()
            )
        )

        return DashboardData(
            learner_df=learner_df,
            segments_df=segments_df,
            kpis=calculate_kpis(
                learner_df
            ),
            risk_metrics=calculate_risk_metrics(
                predictions_df
            ),
            segment_metrics=calculate_segmentation_metrics(
                segments_df
            ),
        )