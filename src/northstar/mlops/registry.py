"""
NorthStar model registry.
"""

from datetime import datetime
from pathlib import Path

from northstar.mlops.loader import ModelLoader
from northstar.mlops.model_metadata import ModelMetadata
from northstar.mlops.model_registry import ModelRegistry

registry = ModelRegistry()

registry.register(
    ModelMetadata(
        name="early_warning",
        version="1.0.0",
        algorithm="RandomForestClassifier",
        task="Binary Classification",
        description="Predicts learners at risk of academic disengagement.",
        registered_at=datetime.now(),
        path=(
            Path(__file__).resolve().parents[1]
            / "early_warning"
            / "models"
            / "early_warning_model.pkl"
        ),
    )
)

registry.register(
    ModelMetadata(
        name="segmentation",
        version="1.0.0",
        algorithm="KMeans",
        task="Clustering",
        description="Segments learners into behavioral cohorts.",
        registered_at=datetime.now(),
        path=(
            Path(__file__).resolve().parents[1]
            / "segmentation"
            / "clustering"
            / "segmentation_model.pkl"
        ),
    )
)

loader = ModelLoader(
    registry,
)