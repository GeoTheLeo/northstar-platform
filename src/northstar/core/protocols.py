"""
Shared Protocol definitions.
"""

from typing import Protocol

import pandas as pd


class DashboardRepositoryProtocol(Protocol):
    """
    Contract for dashboard repositories.
    """

    def load_dashboard_data(
        self,
    ) -> pd.DataFrame:
        """
        Load dashboard data.
        """
        ...


class SegmentationServiceProtocol(Protocol):
    """
    Contract for segmentation services.
    """

    def segment(
        self,
        learner_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Segment learners.
        """
        ...