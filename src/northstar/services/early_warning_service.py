"""
NorthStar Early Warning Service

Provides runtime learner risk prediction.

If no trained model exists, the service trains one automatically.
"""

from pathlib import Path

import joblib
import pandas as pd

from early_warning.features.feature_engineering import create_features
from early_warning.models.train_model import train_model


class EarlyWarningService:
    """
    Runtime inference service for learner risk prediction.
    """

    MODEL_PATH = (
        Path(__file__).resolve().parents[2]
        / "early_warning"
        / "models"
        / "early_warning_model.pkl"
    )

    FEATURE_COLUMNS = [
        "attendance_ratio",
        "engagement_ratio",
        "assessment_ratio",
    ]

    def predict(
        self,
        learner_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Predict learner risk.
        """

        model = self._load_or_train_model(
            learner_df
        )

        engineered = create_features(
            learner_df.copy()
        )

        engineered["risk_prediction"] = model.predict(
            engineered[self.FEATURE_COLUMNS]
        )

        return engineered

    def _load_or_train_model(
        self,
        learner_df: pd.DataFrame,
    ):
        """
        Load an existing model or train one if it does not exist.
        """

        if self.MODEL_PATH.exists():
            return joblib.load(
                self.MODEL_PATH
            )

        model = train_model(
            learner_df.copy()
        )

        return model