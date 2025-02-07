import argparse

from ..services.vespa.core.vespa_service import VespaService
from ..services.vespa.utils.logger import Logger

logger = Logger.get_logger()

# Default test query
DEFAULT_QUERY = """select * from image_search where image_file_name contains "1119015538_e8e796281e.jpg\""""


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Execute generic Vespa queries")
    parser.add_argument(
        "yql",
        type=str,
        nargs="?",  # Makes the argument optional
        default=DEFAULT_QUERY,
        help="YQL query string (default: query for specific image)",
    )
    parser.add_argument(
        "--timeout", type=str, default="3s", help="Query timeout (default: 3s)"
    )
    return parser.parse_args()


def main():
    """Script to test generic Vespa queries."""
    try:
        args = parse_args()

        # Initialize Vespa service
        vespa_service = VespaService()

        logger.info(f"Executing YQL query: '{args.yql}'")

        # Execute query
        results = vespa_service.query(args.yql, timeout=args.timeout)

        # Print raw JSON response
        print("\nQuery Response:")
        print("--------------")
        print(results.json)

    except Exception as e:
        logger.error(f"Query script failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
