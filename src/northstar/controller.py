"""
NorthStar Controller.
"""

from northstar.container import ApplicationContainer
from northstar.models.dashboard_data import DashboardData


class NorthStarController:
    """
    Application controller.
    """

    def __init__(
        self,
    ) -> None:

        self.container = ApplicationContainer()

    def dashboard(
        self,
    ) -> DashboardData:

        return self.container.dashboard_service.load_dashboard()