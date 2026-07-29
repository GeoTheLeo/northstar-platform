"""
CSV Dashboard Repository

Responsible only for loading dashboard source data.
"""

from typing import cast

from pandas import DataFrame

from bi.data.sample_data import load_dashboard_data
from northstar.logging import logger
from northstar.repositories.dashboard_repository import (
    DashboardRepository,
)


class CsvDashboardRepository(DashboardRepository):
    """
    CSV-backed repository.
    """

    def load_dashboard_data(
        self,
    ) -> DataFrame:
        """
        Load learner data.
        """

        logger.info("Using CSV repository.")

        try:
            learner_df = cast(
                DataFrame,
                load_dashboard_data(),
            )

            logger.info(
                "Loaded %d learner records.",
                len(learner_df),
            )

            return learner_df

        except Exception:
            logger.exception(
                "We didn't load learner dataset."
            )
            raise