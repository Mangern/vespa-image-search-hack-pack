import os
from typing import Optional

from dotenv import load_dotenv


class AppConfig:
    """Centralized configuration management for the application."""

    _instance: Optional["AppConfig"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the configuration by loading environment variables."""
        load_dotenv()

        # Vespa Configuration
        self.TARGET = os.getenv("TARGET")

        if self.TARGET == "cloud":
            self.VESPA_TENANT = os.getenv("VESPA_TENANT")
            self.VESPA_APPLICATION = os.getenv("VESPA_APPLICATION")
            self.VESPA_INSTANCE = os.getenv("VESPA_INSTANCE")
            self.VESPA_ENDPOINT = os.getenv("VESPA_ENDPOINT")
            self.VESPA_CERTIFICATE = os.getenv("VESPA_CERTIFICATE")
            self.VESPA_PRIVATE_KEY = os.getenv("VESPA_PRIVATE_KEY")
            self.VESPA_API_KEY = os.getenv("VESPA_API_KEY")
        else:
            self.VESPA_URL = os.getenv("VESPA_URL")
            self.VESPA_PORT = os.getenv("VESPA_PORT")

        # Validate configuration
        self.validate_config()

    def validate_config(self):
        """Validate that all required configuration values are present."""
        if self.TARGET not in ["cloud", "local"]:
            raise ValueError(f"Missing required environment variable TARGET. Possible values: local, cloud")

        if self.TARGET == "cloud":
            required_vars = [
                "VESPA_TENANT",
                "VESPA_APPLICATION",
                "VESPA_INSTANCE",
                "VESPA_ENDPOINT",
                "VESPA_CERTIFICATE",
                "VESPA_PRIVATE_KEY",
            ]
        else:
            required_vars = ["VESPA_URL", "VESPA_PORT"]

        missing_vars = [var for var in required_vars if not getattr(self, var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )


    @staticmethod
    def get_instance() -> "AppConfig":
        """Get the singleton instance of AppConfig."""
        return AppConfig()
