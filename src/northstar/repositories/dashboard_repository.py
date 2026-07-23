"""
Repository interface.
"""

from abc import ABC, abstractmethod

import pandas as pd


class DashboardRepository(ABC):
    """
    Dashboard repository abstraction.
    """

    @abstractmethod
    def load_dashboard_data(
        self,
    ) -> pd.DataFrame:
        """
        Load learner data.
        """
        raise NotImplementedError