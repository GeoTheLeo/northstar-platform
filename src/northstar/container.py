"""
NorthStar Application Container

Creates and wires application services.
"""

from northstar.analysis import DashboardAnalysisService
from northstar.repositories.repository_factory import (
    RepositoryFactory,
)
from northstar.services.dashboard_service import (
    DashboardService,
)


class ApplicationContainer:
    """
    Simple dependency container.
    """

    def __init__(
        self,
    ) -> None:

        repository = (
            RepositoryFactory.create_dashboard_repository()
        )

        analysis = (
            DashboardAnalysisService()
        )

        self.dashboard_service = (
            DashboardService(
                repository=repository,
                analysis=analysis,
            )
        )