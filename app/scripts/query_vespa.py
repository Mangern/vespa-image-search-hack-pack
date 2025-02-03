from ..services.vespa.services.clip_service import ClipService
from ..services.vespa.utils.logger import Logger

logger = Logger.get_logger()


def main():
    """Script to demonstrate CLIP-based image search."""
    try:
        # Initialize CLIP service
        clip_service = ClipService()

        # Example query
        query_text = "A white dog runs in the grass"
        logger.info(f"Performing search with query: '{query_text}'")

        # Perform search
        results = clip_service.search(query_text, hits=5)

        # Print results
        print("\nQuery Results:")
        print("--------------")
        if "root" in results and "children" in results["root"]:
            for hit in results["root"]["children"]:
                print(f"ID: {hit.get('id')}")
                print(f"Relevance: {hit.get('relevance')}")
                if "fields" in hit:
                    print(f"Image: {hit['fields'].get('image_file_name')}")
                print("--------------")
        else:
            print("No results found")

    except Exception as e:
        logger.error(f"Query script failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
