from typing import Dict, List

import clip
import torch

from ..core.vespa_service import VespaService
from ..utils.exceptions import VespaSearchError
from ..utils.logger import Logger

logger = Logger.get_logger()


class ClipService:
    """Service for handling CLIP model operations and image search."""

    def __init__(self, model_name: str = "ViT-B/32", device: str = "cpu"):
        """
        Initialize the CLIP service.

        Args:
            model_name: Name of the CLIP model to use
            device: Device to run the model on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device

        # Load CLIP model
        self.model, _ = clip.load(model_name, device=device)

        # Initialize Vespa service
        self.vespa_service = VespaService()

        # Get model embedding size
        with torch.no_grad():
            # Create a dummy encoding to get embedding size
            dummy_text = clip.tokenize(["test"])
            dummy_features = self.model.encode_text(dummy_text)
            self.embedding_size = dummy_features.shape[1]

        # Register model with the registry
        self.vespa_service.model_registry.register_model(
            name=self.model_name, embedding_size=self.embedding_size
        )

    def encode_text(self, text: str) -> List[float]:
        """
        Encode text query using CLIP model.

        Args:
            text: Text query to encode

        Returns:
            List of normalized embedding values
        """
        try:
            text_tokens = clip.tokenize([text])
            with torch.no_grad():
                text_features = self.model.encode_text(text_tokens).float()
                text_features /= text_features.norm(dim=-1, keepdim=True)

            return text_features.squeeze().tolist()

        except Exception as e:
            logger.error(f"Error encoding text with CLIP: {e}")
            raise VespaSearchError(f"Text encoding failed: {e}")

    def search(self, query_text: str, hits: int = 25) -> Dict:
        """
        Perform a search using the encoded text query.

        Args:
            query_text: Text to search for
            hits: Number of results to return

        Returns:
            Dict containing search results
        """
        try:
            # Encode the query text
            query_embedding = self.encode_text(query_text)

            # Get normalized model name for Vespa
            vespa_model_name = (
                self.model_name.replace("/", "_")
                .replace("-", "_")
                .replace("@", "_")
                .lower()
            )

            logger.info(f"Searching with model: {vespa_model_name}")
            logger.info(f"Embedding size: {len(query_embedding)}")

            # Perform the search
            response = self.vespa_service.search_images(
                query_embedding=query_embedding, model_name=vespa_model_name, hits=hits
            )

            if response.is_successful():
                return response.json
            else:
                raise VespaSearchError("Search query failed")

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VespaSearchError(f"Search operation failed: {e}")
