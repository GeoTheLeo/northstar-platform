"""
Model metadata.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True, frozen=True)
class ModelMetadata:
    """
    Metadata describing a registered model.
    """

    name: str

    version: str

    algorithm: str

    task: str

    description: str

    registered_at: datetime

    path: Path