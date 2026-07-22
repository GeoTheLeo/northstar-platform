from abc import ABC, abstractmethod

from northstar.models.dashboard_data import DashboardData


class DashboardRepository(ABC):
    """
    Abstract interface for dashboard data repositories.
    """

    @abstractmethod
    def load_dashboard(self) -> DashboardData:
        """Load dashboard data."""
        raise NotImplementedError