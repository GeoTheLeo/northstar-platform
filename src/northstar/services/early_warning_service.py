"""
NorthStar Early Warning Service

Provides runtime learner risk prediction.
"""

from typing import Any

import pandas as pd

from northstar.early_warning.features.feature_engineering import (
    create_features,
)
from northstar.early_warning.models.train_model import (
    train_model,
)
from northstar.logging import logger
from northstar.mlops import loader


class EarlyWarningService:
    """
    Runtime inference service.
    """

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

        logger.info(
            "Predicting learner risk for %d learners.",
            len(learner_df),
        )

        model = self._load_or_train_model(
            learner_df,
        )

        engineered = create_features(
            learner_df.copy(),
        )

        engineered["risk_prediction"] = model.predict(
            engineered[self.FEATURE_COLUMNS]
        )

        logger.info(
            "Prediction complete.",
        )

        return engineered

    def _load_or_train_model(
        self,
        learner_df: pd.DataFrame,
    ) -> Any:
        """
        Load an existing model or train one.
        """

        try:

            logger.info(
                "Loading model from registry.",
            )

            return loader.load(
                "early_warning",
            )

        except FileNotFoundError:

            logger.warning(
                "Model not found. Training a new model."
            )

            return train_model(
                learner_df.copy(),
            )