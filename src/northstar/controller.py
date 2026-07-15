"""
NorthStar Platform Controller

Coordinates platform services and exposes
application-ready data to the UI layer.
"""

from northstar.services.dashboard_service import DashboardService


class NorthStarController:
    """
    Application orchestration layer.
    """

    def __init__(self):

        self.dashboard_service = DashboardService()

    def dashboard(self):

        return self.dashboard_service.load_dashboard()