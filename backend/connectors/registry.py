from typing import Optional, TYPE_CHECKING
from core.logging import logger

if TYPE_CHECKING:
    from connectors.base.base_connector import ReadOnlyConnector


# Only implemented connectors — OpenMRS/OpenELIS are not implemented (see ADR-006)
WORKSPACE_CONNECTOR_MAP = {
    "hospital": ["fhir"],
    "community": ["dhis2"],
}

REAL_CONNECTOR_PRIORITY = ["fhir", "dhis2"]


class ConnectorRegistry:
    """Registry of all active connectors.

    Manages connector lifecycle, capability caching, workspace mapping,
    and read-only enforcement. Import-only: not used for interactive queries.
    """

    def __init__(self):
        self._connectors: dict = {}
        self._capability_cache: dict = {}

    def register(self, name: str, connector):
        if not connector.is_connected:
            logger.info(f"Connector {name} not connected — registering but marked inactive")
        self._connectors[name] = connector
        self.refresh_capabilities(name)
        logger.info(f"Connector registered: {name} (read-only: {connector.read_only})")

    def unregister(self, name: str):
        if name in self._connectors:
            self._connectors[name].disconnect()
            del self._connectors[name]
            self._capability_cache.pop(name, None)
            logger.info(f"Connector unregistered: {name}")

    def get(self, name: str):
        return self._connectors.get(name)

    def list(self) -> dict:
        statuses = {}
        for name, conn in self._connectors.items():
            try:
                statuses[name] = conn.health_check()
            except Exception as e:
                statuses[name] = {"status": "error", "error": str(e)}
        return statuses

    def get_by_workspace(self, workspace: str) -> list:
        names = WORKSPACE_CONNECTOR_MAP.get(workspace, [])
        return [self._connectors[n] for n in names if n in self._connectors]

    def get_connected_for_workspace(self, workspace: str) -> list:
        return [c for c in self.get_by_workspace(workspace) if c.is_connected]

    def get_preferred(self, workspace: str) -> Optional["ReadOnlyConnector"]:
        connected = self.get_connected_for_workspace(workspace)
        if not connected:
            return None
        for priority_name in REAL_CONNECTOR_PRIORITY:
            for c in connected:
                if c.name == priority_name:
                    return c
        return connected[0]

    def refresh_capabilities(self, name: Optional[str] = None):
        targets = [name] if name else list(self._connectors.keys())
        for n in targets:
            conn = self._connectors.get(n)
            if not conn or not conn.is_connected:
                continue
            try:
                cap = conn.discover_capabilities()
                self._capability_cache[n] = cap.to_dict()
                logger.info(f"Capabilities refreshed for {n}: {len(cap.supported_resources)} resources")
            except Exception as e:
                logger.warning(f"Capability discovery failed for {n}: {e}")

    def get_capability_cache(self) -> dict:
        return dict(self._capability_cache)

    def connector_count(self) -> int:
        return len(self._connectors)


connector_registry = ConnectorRegistry()
