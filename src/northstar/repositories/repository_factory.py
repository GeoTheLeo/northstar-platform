"""
Repository Factory
"""

from northstar.repositories.csv.dashboard_repository import (
    CsvDashboardRepository,
)


class RepositoryFactory:
    """
    Creates repository implementations.
    """

    @staticmethod
    def create_dashboard_repository():
        return CsvDashboardRepository()