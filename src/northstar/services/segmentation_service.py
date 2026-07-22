"""
NorthStar Segmentation Service

Provides runtime learner segmentation.
"""

import pandas as pd

from segmentation.clustering.train_cluster_model import (
    train_segmentation_model,
)


class SegmentationService:
    """
    Runtime learner segmentation.
    """

    def segment(
        self,
        learner_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate learner segments.
        """

        _, segmented_df = train_segmentation_model(
            learner_df.copy()
        )

        return segmented_df