"""
NorthStar Application Container

Creates and wires application services.
"""

from northstar.repositories.repository_factory import (
    RepositoryFactory,
)
from northstar.services.business_intelligence_service import (
    BusinessIntelligenceService,
)
from northstar.services.dashboard_service import (
    DashboardService,
)
from northstar.services.early_warning_service import (
    EarlyWarningService,
)
from northstar.services.segmentation_service import (
    SegmentationService,
)


class ApplicationContainer:
    """
    Simple dependency container.
    """

    def __init__(self):

        
        repository = (
            RepositoryFactory.create_dashboard_repository()
        )

        early_warning = EarlyWarningService()

        segmentation = SegmentationService()

        business_intelligence = (
            BusinessIntelligenceService()
        )

        self.dashboard_service = DashboardService(
            repository=repository,
            early_warning=early_warning,
            segmentation=segmentation,
            business_intelligence=business_intelligence,
        )