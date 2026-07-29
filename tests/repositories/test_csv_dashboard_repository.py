"""
Tests for CsvDashboardRepository.
"""

import pandas as pd

from northstar.repositories.csv.dashboard_repository import (
    CsvDashboardRepository,
)


def test_load_dashboard_data_returns_dataframe(
    mocker,
):
    """
    Repository should return the DataFrame produced
    by the data loader.
    """

    sample = pd.DataFrame(
        {
            "attendance": [90, 80],
            "engagement_score": [85, 75],
        }
    )

    mocked_loader = mocker.patch(
        "northstar.repositories.csv.dashboard_repository.load_dashboard_data",
        return_value=sample,
    )

    mocked_logger = mocker.patch(
        "northstar.repositories.csv.dashboard_repository.logger"
    )

    repository = CsvDashboardRepository()

    result = repository.load_dashboard_data()

    mocked_loader.assert_called_once()

    pd.testing.assert_frame_equal(
        result,
        sample,
    )

    assert mocked_logger.info.call_count >= 2
