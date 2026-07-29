"""
NorthStar Controller
"""

from northstar.container import ApplicationContainer
from northstar.models.dashboard_data import DashboardData


class NorthStarController:
    """
    Coordinates UI requests.
    """

    def __init__(self) -> None:
        self.container = ApplicationContainer()

    def dashboard(self) -> DashboardData:
        """
        Return the dashboard model for the UI.
        """
        return self.container.dashboard_service.load_dashboard()