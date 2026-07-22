"""
Dashboard Service

Coordinates dashboard data retrieval and business intelligence generation.
"""

from northstar.models.dashboard_data import DashboardData
from northstar.repositories.csv.dashboard_repository import (
    CsvDashboardRepository,
)


class DashboardService:
    """
    Application service responsible for preparing executive dashboard data.

    Responsibilities
    ----------------
    - Retrieve dashboard data from the repository
    - Calculate business metrics
    - Generate executive insights
    """

    def __init__(self):

        self.repository = CsvDashboardRepository()

    def load_dashboard(self) -> DashboardData:
        """
        Load dashboard data and enrich it with executive intelligence.
        """

        dashboard = self.repository.load_dashboard()

        dashboard.executive_summary = self._build_executive_summary(
            dashboard
        )

        return dashboard

    def _build_executive_summary(
        self,
        dashboard: DashboardData,
    ) -> str:
        """
        Generate a concise executive summary.

        This intentionally remains lightweight for now.
        Future sprints will replace these rules with
        AI-assisted insight generation.
        """

        if dashboard.retention_rate >= 90:
            return (
                "Retention is strong. Current customer behaviour "
                "indicates a healthy level of engagement."
            )

        if dashboard.retention_rate >= 80:
            return (
                "Retention remains stable but deserves monitoring "
                "for early warning signals."
            )

        return (
            "Retention has fallen below the desired threshold. "
            "Recommend investigating customer engagement and "
            "identifying at-risk segments."
        )