from etl.loaders.base import BaseLoader
from repositories import HospitalUnitOfWork

HOSPITAL_RESOURCE_ORDER = [
    "hospitals",
    "patients",
    "departments",
    "wards",
    "beds",
    "staff",
    "equipment",
    "medicine_inventory",
    "admissions",
]

# Maps connector resource names → UoW attribute names
HOSPITAL_RESOURCE_MAP = {
    "medicine_inventory": "inventory",
}


class HospitalLoader(BaseLoader):
    UOW_ATTR = "hospitals"

    def __init__(self, db):
        super().__init__(db, HospitalUnitOfWork(db))

    def get_resource_order(self) -> list[str]:
        return HOSPITAL_RESOURCE_ORDER

    def get_uow_attr(self, resource: str) -> str:
        return HOSPITAL_RESOURCE_MAP.get(resource, resource)
