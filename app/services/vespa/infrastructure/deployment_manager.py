from typing import Optional

from vespa.deployment import VespaCloud, VespaDocker
from vespa.package import ApplicationPackage

from ..config.app_config import AppConfig
from ..utils.exceptions import DeploymentError
from ..utils.logger import Logger

logger = Logger.get_logger()


class DeploymentManager:
    """Manages deployment of Vespa applications."""

    def __init__(self):
        """Initialize DeploymentManager with configuration."""
        self.config = AppConfig.get_instance()

    def deploy_application(
        self, app_package: ApplicationPackage, instance: Optional[str] = None
    ) -> None:
        """
        Deploy application package to Vespa Cloud.

        Args:
            app_package: Application package to deploy
            instance: Optional instance name (defaults to config value)
        """
        try:

            if self.config.TARGET == "cloud":
                instance = instance or self.config.VESPA_INSTANCE
                # Initialize VespaCloud with or without key_location based on VESPA_API_KEY
                vespa_cloud_args = {
                    "tenant": self.config.VESPA_TENANT,
                    "application": self.config.VESPA_APPLICATION,
                    "application_package": app_package,
                }

                if self.config.VESPA_API_KEY:
                    vespa_cloud_args["key_location"] = self.config.VESPA_API_KEY

                vespa_cloud = VespaCloud(**vespa_cloud_args)

                logger.info(
                    f"Initiating deployment to Vespa Cloud - "
                    f"Tenant: {self.config.VESPA_TENANT}, "
                    f"Application: {self.config.VESPA_APPLICATION}, "
                    f"Instance: {instance}"
                )

                vespa_cloud.deploy(instance=instance)
                logger.info("Deployment initiated successfully")
            else:
                vespa_container = VespaDocker()

                vespa_container.deploy(application_package=app_package)

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise DeploymentError(f"Failed to deploy application: {e}")
