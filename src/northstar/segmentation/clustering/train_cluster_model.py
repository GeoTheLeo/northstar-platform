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
) -> tuple[KMeans, pd.DataFrame]:
    """
    Train and persist the learner segmentation model.
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