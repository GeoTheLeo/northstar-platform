"""
NorthStar MLOps Layer

Shared infrastructure for all
NorthStar machine learning services.
"""

SUPPORTED_MODELS = [
    "early_warning",
    "segmentation",
    "future_models"
]

SUPPORTED_SERVICES = [
    "training",
    "deployment",
    "monitoring",
    "feature_store",
    "drift_detection"
]