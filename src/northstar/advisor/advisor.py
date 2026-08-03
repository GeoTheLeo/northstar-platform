"""
Executive AI Advisor.
"""

from northstar.advisor.business_rules import (
    generate_recommendations,
)
from northstar.advisor.recommendation import (
    Recommendation,
)
from northstar.models.dashboard_data import (
    DashboardData,
)


class ExecutiveAdvisor:
    """
    Produces executive recommendations from
    dashboard intelligence.
    """

    def advise(
        self,
        dashboard: DashboardData,
    ) -> list[Recommendation]:
        """
        Produce executive recommendations.
        """

        return generate_recommendations(
            dashboard,
        )