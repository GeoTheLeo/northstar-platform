"""
Early Warning prediction service.
"""

import joblib
import pandas as pd

from northstar.core.paths import EARLY_WARNING_MODEL_PATH
from northstar.early_warning.features.feature_engineering import (
    create_features,
)


def predict(
    student_record: dict[str, float],
) -> dict[str, float | int]:
    """
    Predict whether a learner is at risk.
    """

    model = joblib.load(
        EARLY_WARNING_MODEL_PATH,
    )

    df = pd.DataFrame(
        [student_record],
    )

    engineered = create_features(df)

    features = engineered[
        [
            "attendance_ratio",
            "engagement_ratio",
            "assessment_ratio",
        ]
    ]

    prediction = model.predict(
        features,
    )

    probability = model.predict_proba(
        features,
    )

    return {
        "prediction": int(prediction[0]),
        "confidence": float(max(probability[0])),
    }