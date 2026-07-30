"""
NorthStar Learner Segmentation Engine Entry Point.
"""

import pandas as pd

from northstar.segmentation.clustering.train_cluster_model import (
    train_segmentation_model,
)


def main() -> None:
    """Run the learner segmentation pipeline."""

    print("\nNorthStar Learner Segmentation Engine\n")

    df = pd.read_csv("data/raw/learner_segmentation_data.csv")

    _, segmented_data = train_segmentation_model(df)

    print("\nSegmentation completed successfully!\n")

    print(
        segmented_data[
            [
                "student_id",
                "cluster",
            ]
        ].head()
    )


if __name__ == "__main__":
    main()
