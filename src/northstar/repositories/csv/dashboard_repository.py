"""
CSV Dashboard Repository

Responsible only for loading dashboard source data.
"""

from pandas import DataFrame

from bi.data.sample_data import load_dashboard_data

from northstar.repositories.dashboard_repository import (
    DashboardRepository,
)


class CsvDashboardRepository(
    DashboardRepository
):
    """
    CSV-backed repository.
    """

    def load_dashboard_data(
        self,
    ) -> DataFrame:
        """
        Load learner data.
        """

        return load_dashboard_data()