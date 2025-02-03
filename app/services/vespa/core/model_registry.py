from dataclasses import dataclass
from typing import Dict, List, Optional

from ..utils.logger import Logger

logger = Logger.get_logger()


@dataclass
class ModelSpec:
    """Specification for a CLIP model."""

    name: str
    embedding_size: int


class ModelRegistry:
    """Registry for managing CLIP models and their specifications."""

    def __init__(self):
        """Initialize ModelRegistry."""
        self._models: Dict[str, ModelSpec] = {}

    def register_model(self, name: str, embedding_size: int) -> None:
        """
        Register a new model with its specifications.

        Args:
            name: Model name
            embedding_size: Size of the model's embeddings
        """
        normalized_name = self.normalize_model_name(name)
        self._models[normalized_name] = ModelSpec(
            name=name, embedding_size=embedding_size
        )
        logger.info(f"Registered model {name} with embedding size {embedding_size}")

    def get_model_spec(self, name: str) -> Optional[ModelSpec]:
        """Get model specification by name."""
        normalized_name = self.normalize_model_name(name)
        return self._models.get(normalized_name)

    def get_all_models(self) -> List[ModelSpec]:
        """Get all registered models."""
        return list(self._models.values())

    @staticmethod
    def normalize_model_name(name: str) -> str:
        """Normalize model name for Vespa compatibility."""
        return name.replace("/", "_").replace("-", "_").replace("@", "_").lower()
