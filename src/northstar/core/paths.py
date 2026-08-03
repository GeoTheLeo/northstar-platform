"""
Canonical filesystem paths for NorthStar.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SRC_DIR = PROJECT_ROOT / "src"

DATA_DIR = PROJECT_ROOT / "data"

DOCS_DIR = PROJECT_ROOT / "docs"

MODELS_DIR = PROJECT_ROOT / "models"

TESTS_DIR = PROJECT_ROOT / "tests"