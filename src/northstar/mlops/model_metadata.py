"""
Model metadata.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class ModelMetadata:
    """
    Metadata describing a registered model.
    """

    name: str

    version: str

    algorithm: str

    task: str

    description: str

    artifact: str

    status: str

    stage: str

    registered_at: datetime

    path: Path

    load_count: int = 0

    inference_count: int = 0