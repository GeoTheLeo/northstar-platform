"""
Model registry implementation.
"""

from northstar.mlops.model_metadata import ModelMetadata


class ModelRegistry:
    """
    Registry of available machine learning models.
    """

    def __init__(
        self,
    ) -> None:

        self._models: dict[str, ModelMetadata] = {}

    def register(
        self,
        metadata: ModelMetadata,
    ) -> None:
        """
        Register a model.
        """

        self._models[
            metadata.name
        ] = metadata

    def get(
        self,
        name: str,
    ) -> ModelMetadata:
        """
        Retrieve model metadata.
        """

        return self._models[name]

    def names(
        self,
    ) -> list[str]:
        """
        Return registered model names.
        """

        return sorted(
            self._models.keys(),
        )

    def all(
        self,
    ) -> list[ModelMetadata]:
        """
        Return all registered models.
        """

        return sorted(
            self._models.values(),
            key=lambda model: model.name,
        )