"""
Dashboard Repository Interface

Defines the contract for loading dashboard data.
"""

from abc import ABC, abstractmethod

from northstar.models.dashboard_data import DashboardData


class DashboardRepository(ABC):
    """
    Repository abstraction for dashboard data.
    """

    @abstractmethod
    def load_dashboard(self) -> DashboardData:
        """
        Return all information required by the executive dashboard.
        """
        raise NotImplementedError