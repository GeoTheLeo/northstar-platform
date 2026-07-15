import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from early_warning.features.feature_engineering import (
    create_features,
)


def train_model(df: pd.DataFrame):

    df = create_features(df)

    X = df[
        [
            "attendance_ratio",
            "engagement_ratio",
            "assessment_ratio",
        ]
    ]

    y = df["at_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
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

    joblib.dump(
        model,
        "src/early_warning/models/early_warning_model.pkl",
    )

    return model