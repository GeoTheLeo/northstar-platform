"""
Feature Registry
"""

from pandas import DataFrame

from northstar.feature_store.feature_store import (
    FeatureStore,
)
from northstar.feature_store.features import (
    build_engagement_features,
)


class FeatureRegistry:
    """
    Coordinates feature generation for learners.
    """

    def __init__(self) -> None:
        self.store = FeatureStore()

    def learner_features(self) -> DataFrame:
        """
        Load learner data and build the feature set.
        """

        df = self.store.load_students()

        return build_engagement_features(df)