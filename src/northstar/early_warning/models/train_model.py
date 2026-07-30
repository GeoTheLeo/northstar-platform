"""
Early Warning Model Training.
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from northstar.early_warning.features.feature_engineering import (
    create_features,
)

MODEL_PATH = Path(__file__).parent / "early_warning_model.pkl"


def train_model(
    df: pd.DataFrame,
) -> RandomForestClassifier:
    """
    Train and persist the Early Warning model.
    """

    df = create_features(df)

    X = df[
        [
            "attendance_ratio",
            "engagement_ratio",
            "assessment_ratio",
        ]
    ]

    y = df["at_risk"]

    X_train, _X_test, y_train, _y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
    )

    model.fit(X_train, y_train)

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    return model
