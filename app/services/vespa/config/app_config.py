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
        self.TARGET = "local"

        self.VESPA_URL = "http://localhost"
        self.VESPA_PORT = "8080"

    @staticmethod
    def get_instance() -> "AppConfig":
        """Get the singleton instance of AppConfig."""
        return AppConfig()
