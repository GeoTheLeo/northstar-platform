"""
NorthStar Controller
"""

from northstar.container import ApplicationContainer


class NorthStarController:
    """
    Coordinates UI requests.
    """

    def __init__(self):
        self.container = ApplicationContainer()

    def dashboard(self):
        """
        Return the dashboard model for the UI.
        """
        return self.container.dashboard_service.load_dashboard()