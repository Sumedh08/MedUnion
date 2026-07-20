from typing import Optional
from connectors.registry import connector_registry
from connectors.base.base_connector import ReadOnlyConnector
from core.logging import logger


class SourceUnavailableError(Exception):
    """Raised when no connector is available for the requested workspace."""


class MapperRequiredError(Exception):
    """Raised when a non-demo connector has no registered canonical mapper support."""


# Connectors with partial or complete canonical mapper support.
# FHIR/DHIS2 have partial mappers (_map_Patient, _map_Organization,
# _map_organisationUnits). OpenMRS/OpenELIS are not implemented.
MAPPER_READY_CONNECTORS = {
    "fhir",
    "dhis2",
}


class ConnectorResolver:
    """Determines which connector to use for an import.

    ADR: fail-closed for connectors without mapper readiness when preferred.
    """

    def __init__(self, registry=None):
        self._registry = registry or connector_registry

    def resolve(
        self,
        workspace: str,
        preferred: Optional[str] = None,
    ) -> ReadOnlyConnector:
        if preferred:
            conn = self._registry.get(preferred)
            if conn and conn.is_connected:
                self._assert_mapper_ready(conn)
                logger.info(f"Resolver: using preferred connector {preferred} for {workspace}")
                return conn
            logger.info(f"Resolver: preferred connector {preferred} not available, falling back")

        conn = self._registry.get_preferred(workspace)
        if conn:
            self._assert_mapper_ready(conn)
            logger.info(f"Resolver: using {conn.name} for {workspace}")
            return conn

        raise SourceUnavailableError(
            f"No connected connector available for workspace '{workspace}'. "
            f"Registered: {list(self._registry._connectors.keys())}"
        )

    def _assert_mapper_ready(self, conn: ReadOnlyConnector):
        if conn.name not in MAPPER_READY_CONNECTORS:
            raise MapperRequiredError(
                f"Connector '{conn.name}' has no registered canonical mapper. "
                f"Supported for import: {sorted(MAPPER_READY_CONNECTORS)}. "
                f"OpenMRS/OpenELIS are not implemented."
            )

    def list_available(self, workspace: str) -> list[dict]:
        return [
            {
                "name": c.name,
                "connected": c.is_connected,
                "type": type(c).__name__,
                "mapper_ready": c.name in MAPPER_READY_CONNECTORS,
            }
            for c in self._registry.get_by_workspace(workspace)
        ]
