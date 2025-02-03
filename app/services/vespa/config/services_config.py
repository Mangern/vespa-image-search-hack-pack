from vespa.configuration.services import (
    container,
    content,
    document,
    document_api,
    document_processing,
    documents,
    node,
    nodes,
    redundancy,
    search,
    services,
)
from vespa.package import ServicesConfiguration


class ServicesConfig:
    """Configuration for Vespa services."""

    @staticmethod
    def create_services_config(app_name: str = "imagesearch") -> ServicesConfiguration:
        """Create the services configuration."""
        return ServicesConfiguration(
            application_name=app_name,
            services_config=services(
                container(
                    search(),
                    document_api(),
                    document_processing(),
                    id=f"{app_name}_container",
                    version="1.0",
                ),
                content(
                    redundancy("1"),
                    documents(document(type="image_search", mode="index")),
                    nodes(node(distribution_key="0", hostalias="node1")),
                    id=f"{app_name}_content",
                    version="1.0",
                ),
                version="1.0",
            ),
        )
