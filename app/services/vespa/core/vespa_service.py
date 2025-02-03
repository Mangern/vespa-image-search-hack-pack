from typing import Any, Dict, List, Optional

from vespa.io import VespaQueryResponse
from vespa.package import ApplicationPackage

from ..config.schema_config import SchemaConfig
from ..config.services_config import ServicesConfig
from ..core.model_registry import ModelRegistry
from ..core.query_builder import QueryBuilder, QueryConfig
from ..infrastructure.deployment_manager import DeploymentManager
from ..infrastructure.vespa_client import VespaClient
from ..utils.exceptions import VespaSearchError
from ..utils.logger import Logger

logger = Logger.get_logger()


class VespaService:
    """High-level service for Vespa operations."""

    def __init__(self):
        """Initialize VespaService with required components."""
        self.client = VespaClient()
        self.deployment_manager = DeploymentManager()
        self.model_registry = ModelRegistry()

    def initialize_application(
        self, model_embedding_specs: Dict[str, int]
    ) -> ApplicationPackage:
        """
        Initialize a new Vespa application package with given model specifications.

        Args:
            model_embedding_specs: Dictionary mapping model names to embedding sizes

        Returns:
            Configured ApplicationPackage
        """
        try:
            # Create base application package
            app_package = ApplicationPackage(
                name="imagesearch",
                services_config=ServicesConfig.create_services_config(),
            )

            # Set schema name
            app_package.schema.name = "image_search"

            # Add base fields
            app_package.schema.add_fields(*SchemaConfig.create_base_fields())

            # Register and configure models
            for model_name, embedding_size in model_embedding_specs.items():
                # Register model
                self.model_registry.register_model(model_name, embedding_size)

                # Add model-specific fields
                app_package.schema.add_fields(
                    *SchemaConfig.create_model_fields(model_name, embedding_size)
                )

                # Add rank profile
                app_package.schema.add_rank_profile(
                    SchemaConfig.create_rank_profile(model_name, embedding_size)
                )

                # Add query type field
                app_package.query_profile_type.add_fields(
                    SchemaConfig.create_query_type_field(model_name, embedding_size)
                )

            logger.info("Application package initialized successfully")
            return app_package

        except Exception as e:
            logger.error(f"Failed to initialize application package: {e}")
            raise VespaSearchError(f"Application initialization failed: {e}")

    def deploy_application(
        self, app_package: ApplicationPackage, instance: Optional[str] = None
    ) -> None:
        """
        Deploy application package to Vespa Cloud.

        Args:
            app_package: Application package to deploy
            instance: Optional instance name
        """
        try:
            self.deployment_manager.deploy_application(app_package, instance)
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise VespaSearchError(f"Deployment failed: {e}")

    def query(self, yql: str, timeout: str = "3s") -> VespaQueryResponse:
        """
        Execute a YQL query.

        Args:
            yql: YQL query string
            timeout: Query timeout

        Returns:
            VespaQueryResponse containing query results
        """
        try:
            logger.info(f"Executing YQL query: {yql}")
            return self.client.execute_query(yql, timeout=timeout)
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise VespaSearchError(f"Query operation failed: {e}")

    def advanced_query(
        self, query_body: Dict[str, Any], timeout: str = "3s"
    ) -> VespaQueryResponse:
        """
        Execute an advanced query with a complete query body.

        Args:
            query_body: Complete query specification
            timeout: Query timeout

        Returns:
            VespaQueryResponse containing query results
        """
        try:
            logger.info(f"Executing advanced query: {query_body}")
            return self.client.execute_query(query_body, timeout=timeout)
        except Exception as e:
            logger.error(f"Advanced query failed: {e}")
            raise VespaSearchError(f"Advanced query operation failed: {e}")

    def search_images(
        self,
        query_embedding: List[float],
        model_name: str,
        hits: int = 100,
        timeout: str = "3s",
    ) -> VespaQueryResponse:
        """
        Search for images using vector similarity.

        Args:
            query_embedding: Vector embedding for search
            model_name: Name of the model to use
            hits: Number of results to return
            timeout: Query timeout

        Returns:
            VespaQueryResponse containing search results
        """
        try:
            # Get model specification
            model_spec = self.model_registry.get_model_spec(model_name)
            if not model_spec:
                raise VespaSearchError(f"Model {model_name} not found in registry")

            query = QueryBuilder.build_vector_query(
                model_name=model_spec.name,
                query_embedding=query_embedding,
                config=QueryConfig(hits=hits, timeout=timeout),
            )

            return self.client.execute_query(query)

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VespaSearchError(f"Search operation failed: {e}")

    def test_connection(self) -> bool:
        """Test connection to Vespa deployment."""
        return self.client.test_connection()
