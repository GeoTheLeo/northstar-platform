"""
Dashboard Service

Coordinates dashboard data retrieval.
"""

from northstar.models.dashboard_data import DashboardData
from northstar.repositories.csv.dashboard_repository import (
    CsvDashboardRepository,
)


class DashboardService:
    """
    Application service for dashboard data.
    """

    def __init__(self):

        self.repository = CsvDashboardRepository()

    def load_dashboard(self) -> DashboardData:

        return self.repository.load_dashboard()