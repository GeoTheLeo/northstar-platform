"""
Model loader.
"""

from typing import Any

import joblib

from northstar.mlops.model_registry import (
    ModelRegistry,
)


class ModelLoader:
    """
    Loads registered models.
    """

    def __init__(
        self,
        registry: ModelRegistry,
    ) -> None:

        self._registry = registry

    def load(
        self,
        name: str,
    ) -> Any:

        metadata = self._registry.get(
            name,
        )

        return joblib.load(
            metadata.path,
        )