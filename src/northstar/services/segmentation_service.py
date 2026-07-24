"""
NorthStar Segmentation Service

Provides runtime learner segmentation.
"""

import pandas as pd

from segmentation.clustering.train_cluster_model import (
    train_segmentation_model,
)

from northstar.logging import logger


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

        logger.info(
            "Segmenting %d learners.",
            len(learner_df),
        )

        try:

            _, segmented_df = train_segmentation_model(
                learner_df.copy()
            )

            if "cluster" in segmented_df.columns:

                cluster_counts = (
                    segmented_df["cluster"]
                    .value_counts()
                    .sort_index()
                    .to_dict()
                )

                logger.info(
                    "Generated %d learner clusters.",
                    len(cluster_counts),
                )

                logger.info(
                    "Cluster distribution: %s",
                    cluster_counts,
                )

            logger.info(
                "Learner segmentation complete."
            )

            return segmented_df

        except Exception:

            logger.exception(
                "Learner segmentation failed."
            )

            raise