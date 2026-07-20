from enum import Enum
from typing import Optional


class WorkspaceType(str, Enum):
    HOSPITAL = "hospital"
    COMMUNITY = "community"


class Workspace:
    """Represents an active workspace with its own domain model, connectors, and KPIs."""

    def __init__(self, workspace_type: WorkspaceType, name: str, description: str):
        self.type = workspace_type
        self.name = name
        self.description = description
        self._connector_names: list[str] = []

    def add_connector(self, name: str):
        self._connector_names.append(name)

    @property
    def connector_names(self) -> list[str]:
        return list(self._connector_names)

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "connectors": self._connector_names,
        }


class WorkspaceRegistry:
    """Registry of all available workspaces.

    Each workspace maps to a separate domain model, connector set, KPI set,
    and navigation structure. Switching workspaces switches the entire data model.
    """

    def __init__(self):
        self._workspaces: dict[str, Workspace] = {}
        self._active: Optional[str] = None

    def register(self, workspace: Workspace):
        self._workspaces[workspace.type.value] = workspace
        if self._active is None:
            self._active = workspace.type.value

    def get(self, workspace_type: str) -> Optional[Workspace]:
        return self._workspaces.get(workspace_type)

    @property
    def active(self) -> Optional[Workspace]:
        return self._workspaces.get(self._active) if self._active else None

    def switch_to(self, workspace_type: str) -> bool:
        if workspace_type in self._workspaces:
            self._active = workspace_type
            return True
        return False

    def list_all(self) -> list[dict]:
        return [w.to_dict() for w in self._workspaces.values()]

    def to_dict(self) -> dict:
        return {
            "active": self._active,
            "workspaces": self.list_all(),
        }


workspace_registry = WorkspaceRegistry()


def init_workspaces():
    """Register default workspaces."""
    hospital = Workspace(
        WorkspaceType.HOSPITAL,
        "Hospital Intelligence",
        "Hospital operations command center. Monitor beds, patients, staff, equipment, and medicines.",
    )
    hospital.add_connector("fhir")

    community = Workspace(
        WorkspaceType.COMMUNITY,
        "Community Health Intelligence",
        "Population health intelligence. Disease surveillance, vaccination coverage, medicine distribution.",
    )
    community.add_connector("dhis2")

    workspace_registry.register(hospital)
    workspace_registry.register(community)
    return workspace_registry
