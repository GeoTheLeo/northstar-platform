"""
Early Warning Model Training.
"""

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from northstar.core.paths import EARLY_WARNING_MODEL_PATH
from northstar.early_warning.features.feature_engineering import (
    create_features,
)


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

    model.fit(
        X_train,
        y_train,
    )

    EARLY_WARNING_MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        EARLY_WARNING_MODEL_PATH,
    )

    return model