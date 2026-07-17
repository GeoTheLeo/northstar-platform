"""
Central Feature Store

Provides reusable engineered features
for all predictive models.
"""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]


class FeatureStore:
    """
    Central access point for engineered features.
    """

    def load_students(self) -> pd.DataFrame:

        return pd.read_csv(
            BASE_DIR
            / "data"
            / "raw"
            / "student_data.csv"
        )

    def load_segmentation(self) -> pd.DataFrame:

        return pd.read_csv(
            BASE_DIR
            / "data"
            / "raw"
            / "learner_segmentation_data.csv"
        )