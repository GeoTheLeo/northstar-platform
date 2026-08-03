"""
Canonical filesystem paths for NorthStar.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SRC_DIR = PROJECT_ROOT / "src"

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

DOCS_DIR = PROJECT_ROOT / "docs"

MODELS_DIR = PROJECT_ROOT / "models"

TESTS_DIR = PROJECT_ROOT / "tests"

EARLY_WARNING_MODEL_PATH = (
    SRC_DIR
    / "northstar"
    / "early_warning"
    / "models"
    / "early_warning_model.pkl"
)

SEGMENTATION_MODEL_PATH = (
    SRC_DIR
    / "northstar"
    / "segmentation"
    / "clustering"
    / "segmentation_model.pkl"
)

STUDENT_DATA_PATH = (
    RAW_DATA_DIR
    / "student_data.csv"
)

SEGMENTATION_DATA_PATH = (
    RAW_DATA_DIR
    / "learner_segmentation_data.csv"
)