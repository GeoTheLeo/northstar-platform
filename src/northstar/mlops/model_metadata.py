"""
Model metadata.
"""

from dataclasses import dataclass
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

    path: Path