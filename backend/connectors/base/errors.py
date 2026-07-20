class ConnectorError(Exception):
    """Base exception for all connector errors."""


class ConnectionFailedError(ConnectorError):
    """Raised when a connector cannot establish a connection."""


class AuthenticationError(ConnectorError):
    """Raised when authentication fails."""


class ReadOnlyViolationError(ConnectorError):
    """Raised when a write operation is attempted on a read-only connector."""


class ResourceNotFoundError(ConnectorError):
    """Raised when a requested resource is not found."""


class CapabilityDiscoveryError(ConnectorError):
    """Raised when capability discovery fails."""


class RateLimitError(ConnectorError):
    """Raised when the external API rate limit is exceeded."""


class TimeoutError(ConnectorError):
    """Raised when a request times out."""


class PaginationError(ConnectorError):
    """Raised when pagination fails."""


class SchemaMappingError(ConnectorError):
    """Raised when schema mapping fails."""
