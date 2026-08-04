"""
Model registry implementation.
"""

from pathlib import Path

from northstar.mlops.model_metadata import (
    ModelMetadata,
)


class ModelRegistry:
    """
    Registry of available models.
    """

    def __init__(
        self,
    ) -> None:

        self._models: dict[str, ModelMetadata] = {}

    def register(
        self,
        metadata: ModelMetadata,
    ) -> None:

        self._models[
            metadata.name
        ] = metadata

    def get(
        self,
        name: str,
    ) -> ModelMetadata:

        return self._models[name]

    def names(
        self,
    ) -> list[str]:

        return sorted(
            self._models.keys(),
        )