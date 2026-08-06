"""
Dashboard Service

Loads dashboard data and delegates analysis.
"""

from northstar.analysis import DashboardAnalysisService
from northstar.logging import logger
from northstar.models.dashboard_data import DashboardData
from northstar.repositories.csv.dashboard_repository import (
    CsvDashboardRepository,
)


class DashboardService:
    """
    Coordinates dashboard generation.
    """

    def __init__(
        self,
        repository: CsvDashboardRepository | None = None,
        analysis: DashboardAnalysisService | None = None,
    ) -> None:

        self.repository = (
            repository
            if repository is not None
            else CsvDashboardRepository()
        )

        self.analysis = (
            analysis
            if analysis is not None
            else DashboardAnalysisService()
        )

    def load_dashboard(
        self,
    ) -> DashboardData:
        """
        Load dashboard data.
        """

        logger.info(
            "Loading dashboard."
        )

        learner_df = (
            self.repository.load_dashboard_data()
        )

        dashboard = self.analysis.analyse(
            learner_df,
        )

        logger.info(
            "Dashboard ready."
        )

        return dashboard