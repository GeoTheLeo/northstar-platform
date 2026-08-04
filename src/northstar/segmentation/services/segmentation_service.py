"""
Segmentation inference service.
"""

from typing import Any

import pandas as pd

from northstar.mlops import loader
from northstar.segmentation.features.feature_engineering import (
    create_features,
)


class SegmentationPredictionService:
    """
    Runtime segmentation inference.
    """

    FEATURE_COLUMNS = [
        "attendance_ratio",
        "engagement_ratio",
        "assessment_ratio",
    ]

    def assign_cluster(
        self,
        learner_record: dict[str, float],
    ) -> dict[str, int]:
        """
        Predict learner cluster.
        """

        model = self._load_model()

        df = pd.DataFrame(
            [learner_record],
        )

        engineered = create_features(
            df,
        )

        cluster = model.predict(
            engineered[self.FEATURE_COLUMNS]
        )

        return {
            "cluster": int(cluster[0]),
        }

    def _load_model(
        self,
    ) -> Any:
        """
        Load the segmentation model.
        """

        return loader.load(
            "segmentation",
        )