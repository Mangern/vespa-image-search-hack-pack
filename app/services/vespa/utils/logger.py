import logging
import sys
from typing import Optional


class Logger:
    """Centralized logging configuration."""

    _instance: Optional[logging.Logger] = None

    @staticmethod
    def setup(
        name: str = "vespa_search",
        level: int = logging.INFO,
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    ) -> logging.Logger:
        """Set up and configure logger."""
        if Logger._instance is None:
            logger = logging.getLogger(name)
            logger.setLevel(level)

            # Create console handler
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(level)

            # Create formatter
            formatter = logging.Formatter(log_format)
            handler.setFormatter(formatter)

            # Add handler to logger
            logger.addHandler(handler)

            Logger._instance = logger

        return Logger._instance

    @staticmethod
    def get_logger() -> logging.Logger:
        """Get the configured logger instance."""
        if Logger._instance is None:
            return Logger.setup()
        return Logger._instance
