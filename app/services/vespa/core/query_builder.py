from dataclasses import dataclass
from typing import Dict, List, Optional

from ..utils.logger import Logger

logger = Logger.get_logger()


@dataclass
class QueryConfig:
    """Configuration for query construction."""

    hits: int = 100
    timeout: str = "3s"


class QueryBuilder:
    """Builds Vespa queries for image search."""

    @staticmethod
    def build_vector_query(
        model_name: str,
        query_embedding: List[float],
        config: Optional[QueryConfig] = None,
    ) -> Dict:
        """
        Build a vector search query.

        Args:
            model_name: Name of the model
            query_embedding: Vector embedding for search
            config: Optional query configuration

        Returns:
            Dict containing the complete query
        """
        config = config or QueryConfig()
        model_field = (
            model_name.replace("/", "_").replace("-", "_").replace("@", "_").lower()
        )

        return {
            "yql": f'select * from sources * where ({{"targetNumHits":{config.hits}}}nearestNeighbor({model_field}_image,q))',
            "hits": config.hits,
            "timeout": config.timeout,
            "ranking.profile": f"{model_field}_similarity",
            "input.query(q)": {"values": query_embedding},
        }
