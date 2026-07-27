"""
Shared pytest fixtures for NorthStar.
"""

import pandas as pd
import pytest


@pytest.fixture
def learner_dataframe():
    """
    Representative learner dataset used across tests.
    """

    return pd.DataFrame(
        {
            "attendance": [95, 72, 88, 61],
            "engagement_score": [91, 63, 84, 55],
            "assessment_score": [89, 58, 81, 49],
        }
    )