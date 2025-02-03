from dataclasses import dataclass
from typing import List

from vespa.package import HNSW, Field, QueryTypeField, RankProfile


@dataclass
class SchemaConfig:
    """Configuration for Vespa schema."""

    schema_name: str = "image_search"

    @staticmethod
    def create_base_fields() -> List[Field]:
        """Create base fields for the schema."""
        return [
            Field(
                name="image_file_name", type="string", indexing=["attribute", "summary"]
            )
        ]

    @staticmethod
    def create_model_fields(model_name: str, embedding_size: int) -> List[Field]:
        """Create fields for a specific model."""
        valid_model_name = SchemaConfig.normalize_model_name(model_name)

        return [
            Field(
                name=f"{valid_model_name}_image",
                type=f"tensor<float>(x[{embedding_size}])",
                indexing=["attribute", "index"],
                ann=HNSW(
                    distance_metric="euclidean",
                    max_links_per_node=16,
                    neighbors_to_explore_at_insert=200,
                ),
            )
        ]

    @staticmethod
    def create_rank_profile(model_name: str, embedding_size: int) -> RankProfile:
        """Create rank profile for a specific model."""
        valid_model_name = SchemaConfig.normalize_model_name(model_name)

        return RankProfile(
            name=f"{valid_model_name}_similarity",
            inherits="default",
            first_phase=f'closeness("field", {valid_model_name}_image)',
            inputs=[("q", f"tensor<float>(x[{embedding_size}])")],
        )

    @staticmethod
    def create_query_type_field(model_name: str, embedding_size: int) -> QueryTypeField:
        """Create query type field for a specific model."""
        valid_model_name = SchemaConfig.normalize_model_name(model_name)

        return QueryTypeField(
            name=f"ranking.features.query({valid_model_name}_text)",
            type=f"tensor<float>(x[{embedding_size}])",
        )

    @staticmethod
    def normalize_model_name(model_name: str) -> str:
        """Normalize model name to be valid in Vespa."""
        return model_name.replace("/", "_").replace("-", "_").replace("@", "_").lower()
