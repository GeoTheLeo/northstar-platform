import joblib
import pandas as pd

from segmentation.features.feature_engineering import (
    create_features,
)

MODEL_PATH = "src/segmentation/clustering/segmentation_model.pkl"


def assign_cluster(
    learner_record: dict,
):

    model = joblib.load(MODEL_PATH)

    df = pd.DataFrame([learner_record])

    df = create_features(df)

    X = df[
        [
            "attendance_ratio",
            "engagement_ratio",
            "assessment_ratio",
        ]
    ]

    cluster = model.predict(X)

    return {"cluster": int(cluster[0])}
