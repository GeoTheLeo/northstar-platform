"""
Segmentation prediction service.
"""

from pathlib import Path
from typing import TypedDict

import joblib
import pandas as pd

from northstar.segmentation.features.feature_engineering import (
    create_features,
)

MODEL_PATH = Path(__file__).parent.parent / "clustering" / "segmentation_model.pkl"


class ClusterPrediction(TypedDict):
    """
    Result returned by the segmentation model.
    """

    cluster: int


class LearnerRecord(TypedDict):
    """
    Input learner record for clustering.
    """

    attendance: float
    engagement_score: float
    assessment_score: float


def assign_cluster(
    learner_record: LearnerRecord,
) -> ClusterPrediction:
    """
    Assign a learner to a cluster.

    Parameters
    ----------
    learner_record:
        Dictionary describing a single learner.

    Returns
    -------
    ClusterPrediction
        Predicted learner cluster.
    """

    model = joblib.load(MODEL_PATH)

    df = pd.DataFrame([learner_record])

    engineered = create_features(df)

    features = engineered[
        [
            "attendance_ratio",
            "engagement_ratio",
            "assessment_ratio",
        ]
    ]

    cluster = model.predict(features)

    return ClusterPrediction(
        cluster=int(cluster[0]),
    )