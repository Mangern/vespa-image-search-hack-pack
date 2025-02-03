from typing import Optional

from app.services.vespa.infrastructure.vespa_client import VespaClient

from ...services.vespa.utils.logger import Logger

logger = Logger.get_logger()

vespa_client = VespaClient()

def register_routes(rt):
    @rt("/api/search")
    def get(query: Optional[str] = None):
        """Search endpoint that uses CLIP service to find relevant images."""
        try:
            if not query:
                return {"images": []}

            logger.info(f"Searching for: {query}")
            results = vespa_client.execute_query({
                "input": query,
                "hits": 25
            }).json

            # Log the first result to see its structure
            if (
                "root" in results
                and "children" in results["root"]
                and results["root"]["children"]
            ):
                logger.info(f"First result: {results['root']['children'][0]}")

            # Extract image paths and ensure they're in the correct format
            # The component will add /dataset/ prefix, so we just need flickr8k/image.webp format
            images = []
            if "root" in results and "children" in results["root"]:
                for hit in results["root"]["children"]:
                    image_name = hit["fields"].get("image_file_name")
                    if image_name:
                        # Make sure path is in correct format relative to dataset directory
                        image_path = (
                            f"flickr8k/{image_name}"
                            if not image_name.startswith("flickr8k/")
                            else image_name
                        )
                        images.append(image_path)

            logger.info(f"Returning {len(images)} images")
            if images:
                logger.info(f"First image path: {images[0]}")

            return {"images": images}

        except Exception as e:
            logger.error(f"Search API error: {e}")
            return {"error": str(e)}, 500
