import joblib
import pandas as pd

from early_warning.features.feature_engineering import (
    create_features,
)

MODEL_PATH = "src/early_warning/models/early_warning_model.pkl"


def predict(student_record: dict):

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
        "confidence": float(max(probability[0])),
    }
