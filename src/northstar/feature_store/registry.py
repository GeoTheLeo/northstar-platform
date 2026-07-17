"""
Feature Registry
"""

from northstar.feature_store.feature_store import (
    FeatureStore,
)

from northstar.feature_store.features import (
    build_engagement_features,
)


class FeatureRegistry:

    def __init__(self):

        self.store = FeatureStore()

    def learner_features(self):

        df = self.store.load_students()

        return build_engagement_features(df)