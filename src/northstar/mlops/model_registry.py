"""
Model registry implementation.
"""

from northstar.mlops.model_metadata import ModelMetadata


class ModelRegistry:
    """
    Registry of machine learning models.
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

    def all(
        self,
    ) -> list[ModelMetadata]:

        return sorted(
            self._models.values(),
            key=lambda model: model.name,
        )

    def increment_load(
        self,
        name: str,
    ) -> None:

        self._models[name].load_count += 1

    def increment_inference(
        self,
        name: str,
    ) -> None:

        self._models[name].inference_count += 1