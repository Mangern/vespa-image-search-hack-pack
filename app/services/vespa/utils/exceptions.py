class VespaSearchError(Exception):
    """Base exception for Vespa search application."""

    pass


class ConfigurationError(VespaSearchError):
    """Raised when there's a configuration error."""

    pass


class VespaConnectionError(VespaSearchError):
    """Raised when there's an error connecting to Vespa."""

    pass


class QueryError(VespaSearchError):
    """Raised when there's an error with query construction or execution."""

    pass


class DeploymentError(VespaSearchError):
    """Raised when there's an error during deployment."""

    pass
