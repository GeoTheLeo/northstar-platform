import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

sys.path.append(
    str(project_root / "src")
)

import pandas as pd

from segmentation.clustering.train_cluster_model import (
    train_segmentation_model,
)

print(
    "\nNorthStar Learner Segmentation Engine\n"
)

df = pd.read_csv(
    "data/raw/learner_segmentation_data.csv"
)

model, segmented_data = (
    train_segmentation_model(df)
)

print(
    "\nSegmentation completed successfully!\n"
)

print(
    segmented_data[
        [
            "student_id",
            "cluster",
        ]
    ].head()
)