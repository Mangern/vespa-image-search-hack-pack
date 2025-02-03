from typing import List, Optional

import httpx
from fasthtml.common import Title

from ...components.search_results import EmptySearchResults, search_results_grid
from ...layouts.app_layout import app_layout
from .search_box import toolbar_search_box


def build_search_response(
    images: List = None, query: str = "", animation_config: dict = None
):
    """Build the search response with consistent grid configuration."""
    if animation_config is None:
        animation_config = {
            "duration": 0.8,
            "ease": "power3.out",
            "scale": 2.2,
            "spread": 120,
            "max_rotation": 6,
            "max_distance": 800,
            "gap": 13,
        }

    content = (
        search_results_grid(images, **animation_config)
        if images
        else EmptySearchResults(query=query)
    )

    return (
        Title("Image Search Explorer"),
        app_layout(
        content,
        with_toolbar=True,
        toolbar_attrs={
            "content": toolbar_search_box(query),
            "cls": "!px-0",
        },
    ))


def register_routes(rt):
    @rt("/search")
    def get(query: Optional[str] = None):
        if not query:
            return build_search_response()

        try:
            # Call our search API endpoint with explicit base URL
            response = httpx.get(
                "http://localhost:5001/api/search", params={"query": query}, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            return build_search_response(images=data.get("images", []), query=query)

        except Exception:
            # Return empty results while preserving the query
            return build_search_response(query=query)
