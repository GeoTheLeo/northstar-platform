"""
Early Warning prediction service.
"""

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from northstar.early_warning.features.feature_engineering import (
    create_features,
)

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "early_warning_model.pkl"
)


def predict(student_record: dict[str, Any]) -> dict[str, float | int]:
    """
    Generate an Early Warning prediction for a single learner.
    """

    model = joblib.load(MODEL_PATH)

    df = pd.DataFrame([student_record])

    df = create_features(df)

    X = df[
        [
            "attendance_ratio",
            "engagement_ratio",
            "assessment_ratio",
        ]
    ]

    prediction = model.predict(X)

    probability = model.predict_proba(X)

    return {
        "prediction": int(prediction[0]),
        "confidence": float(probability[0].max()),
    }
