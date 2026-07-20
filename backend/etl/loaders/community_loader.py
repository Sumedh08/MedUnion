from etl.loaders.base import BaseLoader
from repositories import CommunityUnitOfWork

COMMUNITY_RESOURCE_ORDER = [
    "districts",
    "facilities",
    "disease_reports",
    "outbreaks",
    "health_workers",
    "vaccinations",
    "medicine_stock",
    "indicators",
    "surveillance_events",
]

COMMUNITY_RESOURCE_MAP = {
    "disease_reports": "disease_cases",
}


class CommunityLoader(BaseLoader):
    UOW_ATTR = "communities"

    def __init__(self, db):
        super().__init__(db, CommunityUnitOfWork(db))

    def get_resource_order(self) -> list[str]:
        return COMMUNITY_RESOURCE_ORDER

    def get_uow_attr(self, resource: str) -> str:
        return COMMUNITY_RESOURCE_MAP.get(resource, resource)
