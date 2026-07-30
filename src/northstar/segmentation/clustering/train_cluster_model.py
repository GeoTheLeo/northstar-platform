"""
Learner Segmentation Model Training.
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.cluster import KMeans

from northstar.segmentation.features.feature_engineering import (
    create_features,
)

MODEL_PATH = Path(__file__).parent / "segmentation_model.pkl"


def train_segmentation_model(
    df: pd.DataFrame,
) -> tuple[KMeans, pd.DataFrame]:
    """
    Train the learner segmentation model and persist it to disk.

    Returns:
        A tuple containing the trained KMeans model and the input
        DataFrame augmented with cluster assignments.
    """

    df = create_features(df)

    X = df[
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

    clusters = model.fit_predict(X)

    df["cluster"] = clusters

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    return model, df