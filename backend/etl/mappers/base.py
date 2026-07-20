from abc import ABC, abstractmethod
from typing import Any


class CanonicalMapper(ABC):
    """Transforms connector-native records into canonical domain dicts.

    Each method maps a specific resource type.
    Repositories only receive canonical dicts — never raw connector data.
    """

    @abstractmethod
    def map(self, resource: str, records: list[dict]) -> list[dict]:
        ...


class BaseCanonicalMapper(CanonicalMapper):
    """Pass-through mapper where connector fields already match DB columns.

    Override specific resource methods for non-trivial mappings (e.g., FHIR → domain).
    """

    def map(self, resource: str, records: list[dict]) -> list[dict]:
        method = getattr(self, f"_map_{resource}", None)
        if method:
            return method(records)
        return records

    def _map_field(self, record: dict, mapping: dict[str, str]) -> dict:
        return {target: record.get(source) for source, target in mapping.items()}
