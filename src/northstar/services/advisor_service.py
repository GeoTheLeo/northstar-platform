"""
Advisor Service.

Application service responsible for
executive decision support.
"""

from northstar.advisor import ExecutiveAdvisor
from northstar.advisor.recommendation import Recommendation
from northstar.mlops.registry import registry
from northstar.models.dashboard_data import DashboardData


class AdvisorService:
    """
    Application layer wrapper around the
    Executive AI Advisor.
    """

    def __init__(
        self,
    ) -> None:

        self._advisor = ExecutiveAdvisor()

    def advise(
        self,
        dashboard: DashboardData,
    ) -> list[Recommendation]:
        """
        Produce executive recommendations.
        """

        return self._advisor.advise(
            dashboard,
        )

    def registered_models(
        self,
    ) -> list[str]:
        """
        Return registered model names.
        """

        return registry.names()