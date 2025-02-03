from typing import Any, Dict, Union

from vespa.application import Vespa
from vespa.exceptions import VespaError
from vespa.io import VespaQueryResponse

from ..config.app_config import AppConfig
from ..utils.exceptions import QueryError, VespaConnectionError
from ..utils.logger import Logger

logger = Logger.get_logger()


class VespaClient:
    """Client for interacting with Vespa deployment."""

    def __init__(self):
        """Initialize VespaClient with configuration."""
        self.config = AppConfig.get_instance()
        self._vespa_app = self._initialize_vespa_app()

    def _initialize_vespa_app(self) -> Vespa:
        """Initialize Vespa application instance."""
        try:
            if self.config.TARGET == "cloud":
                return Vespa(
                    url=self.config.VESPA_ENDPOINT,
                    cert=self.config.VESPA_CERTIFICATE,
                    key=self.config.VESPA_PRIVATE_KEY,
                )
            else:
                return Vespa(
                    url=self.config.VESPA_URL,
                    port=int(self.config.VESPA_PORT)
                )
        except Exception as e:
            logger.error(f"Failed to initialize Vespa client: {e}")
            raise VespaConnectionError(f"Failed to initialize Vespa client: {e}")

    @property
    def vespa_app(self) -> Vespa:
        """Get the Vespa application instance."""
        return self._vespa_app

    def execute_query(
        self, query: Union[str, Dict[str, Any]], timeout: str = "3s"
    ) -> VespaQueryResponse:
        """
        Execute a query against Vespa. Supports both YQL strings and query bodies.

        Args:
            query: Either a YQL query string or a complete query body dictionary
            timeout: Query timeout duration

        Returns:
            VespaQueryResponse object containing query results
        """
        try:
            # Construct query body based on input type
            if isinstance(query, str):
                query_body = {"yql": query}
            else:
                query_body = query

            # Add timeout to query body if not present
            if "timeout" not in query_body:
                query_body["timeout"] = timeout

            logger.info(f"Executing query with body: {query_body}")

            with self._vespa_app.syncio() as session:
                response = session.query(body=query_body)

            if response.is_successful():
                logger.info("Query executed successfully")
                return response
            else:
                raise QueryError(
                    f"Query failed with status code: {response.status_code}"
                )

        except VespaError as e:
            logger.error(f"Vespa query error: {e}")
            raise QueryError(f"Failed to execute query: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {e}")
            raise QueryError(f"Unexpected error during query execution: {e}")

    def test_connection(self) -> bool:
        """Test connection to Vespa deployment."""
        try:
            response = self._vespa_app.get_application_status()
            logger.info("Vespa connection test successful")
            return True
        except Exception as e:
            logger.error(f"Vespa connection test failed: {e}")
            raise VespaConnectionError(f"Failed to connect to Vespa: {e}")
