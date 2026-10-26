"""
Learner Segmentation Model Training.
"""

import joblib
import pandas as pd
from sklearn.cluster import KMeans

from northstar.core.paths import SEGMENTATION_MODEL_PATH
from northstar.segmentation.features.feature_engineering import (
    create_features,
)


def train_segmentation_model(
    df: pd.DataFrame,
    persist: bool = True,
) -> tuple[KMeans, pd.DataFrame]:
    """
    Train the learner segmentation model, persisting it unless persist=False.

    Runtime callers (the dashboard) pass persist=False: the saved artifact is
    what the inference API serves, so only the training script may write it.
    """

    engineered = create_features(df)

    features = engineered[
        [
            "attendance_ratio",
            "engagement_ratio",
            "assessment_ratio",
        ]
    ]

    model = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10,
    )

    engineered["cluster"] = model.fit_predict(
        features,
    )

    if persist:
        SEGMENTATION_MODEL_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            model,
            SEGMENTATION_MODEL_PATH,
        )

    return (
        model,
        engineered,
    )