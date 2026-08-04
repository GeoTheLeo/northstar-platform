"""
NorthStar Model Registry.

Registers all machine learning models available
within the NorthStar platform.
"""

from datetime import datetime
from pathlib import Path

from northstar.mlops.loader import ModelLoader
from northstar.mlops.model_metadata import ModelMetadata
from northstar.mlops.model_registry import ModelRegistry

registry = ModelRegistry()

# ---------------------------------------------------------------------
# Early Warning Model
# ---------------------------------------------------------------------

registry.register(
    ModelMetadata(
        name="early_warning",
        version="1.0.0",
        algorithm="RandomForestClassifier",
        task="Binary Classification",
        description=(
            "Predicts learners at risk of academic disengagement."
        ),
        artifact="early_warning_model.pkl",
        status="ACTIVE",
        stage="Production",
        registered_at=datetime.now(),
        path=(
            Path(__file__).resolve().parents[1]
            / "early_warning"
            / "models"
            / "early_warning_model.pkl"
        ),
    )
)

# ---------------------------------------------------------------------
# Learner Segmentation Model
# ---------------------------------------------------------------------

registry.register(
    ModelMetadata(
        name="segmentation",
        version="1.0.0",
        algorithm="KMeans",
        task="Clustering",
        description=(
            "Segments learners into behavioral cohorts."
        ),
        artifact="segmentation_model.pkl",
        status="ACTIVE",
        stage="Production",
        registered_at=datetime.now(),
        path=(
            Path(__file__).resolve().parents[1]
            / "segmentation"
            / "clustering"
            / "segmentation_model.pkl"
        ),
    )
)

# ---------------------------------------------------------------------
# Shared Loader
# ---------------------------------------------------------------------

loader = ModelLoader(
    registry,
)