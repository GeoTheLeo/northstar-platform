import joblib
import pandas as pd

from sklearn.cluster import KMeans

from segmentation.features.feature_engineering import (
    create_features,
)


def train_segmentation_model(
    df: pd.DataFrame,
):

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

    joblib.dump(
        model,
        "src/segmentation/clustering/segmentation_model.pkl",
    )

    return model, df