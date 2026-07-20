from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import datetime
from core.logging import logger
from connectors.base.errors import ReadOnlyViolationError


class CapabilityStatement:
    """Describes what a connector can do."""

    def __init__(
        self,
        connector_type: str,
        api_version: str,
        supported_resources: list[str],
        supported_operations: list[str],
        metadata: Optional[dict] = None,
    ):
        self.connector_type = connector_type
        self.api_version = api_version
        self.supported_resources = supported_resources
        self.supported_operations = supported_operations
        self.metadata = metadata or {}
        self.discovered_at = datetime.utcnow()
        self.is_valid = True

    def to_dict(self) -> dict:
        return {
            "connector_type": self.connector_type,
            "api_version": self.api_version,
            "supported_resources": self.supported_resources,
            "supported_operations": self.supported_operations,
            "metadata": self.metadata,
            "discovered_at": self.discovered_at.isoformat(),
            "is_valid": self.is_valid,
        }


class ReadOnlyConnector(ABC):
    """Abstract base for all read-only healthcare data connectors.

    Every connector enforces read-only access. Write operations (POST, PUT,
    PATCH, DELETE) are not exposed in this interface. Attempting to call
    them will raise ReadOnlyViolationError.
    """

    name: str = "base"
    config: dict = {}

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self._connected = False
        self._capabilities: Optional[CapabilityStatement] = None

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the external system."""

    @abstractmethod
    def disconnect(self):
        """Close the connection."""

    @abstractmethod
    def health_check(self) -> dict:
        """Return connector health status."""

    @abstractmethod
    def discover_capabilities(self) -> CapabilityStatement:
        """Discover available resources and capabilities."""

    @abstractmethod
    def fetch(self, resource: str, params: Optional[dict] = None) -> list[dict]:
        """Fetch resources. Read-only. Raises ReadOnlyViolationError for write attempts."""

    def get_capabilities(self) -> Optional[CapabilityStatement]:
        return self._capabilities

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def read_only(self) -> bool:
        return True

    def assert_read_only(self, method: str):
        if method.upper() in ("POST", "PUT", "PATCH", "DELETE", "UPSERT"):
            from connectors.base.errors import ReadOnlyViolationError
            raise ReadOnlyViolationError(
                f"Read-only connector: {method} operations are forbidden. "
                f"This platform never modifies external healthcare systems."
            )


class ReadOnlyMixin:
    """Mixin that enforces read-only access at the method level."""

    def assert_read_only(self, method: str):
        if method.upper() in ("POST", "PUT", "PATCH", "DELETE", "UPSERT"):
            raise ReadOnlyViolationError(
                f"Read-only connector: {method} operations are forbidden. "
                f"This platform never modifies external healthcare systems."
            )
