from repositories.base import BaseRepository
from models.community.geography import District, Province, Country
from models.community.health import HealthFacility, HealthWorker, HealthProgram
from models.community.surveillance import Disease, DiseaseCase, Outbreak, SurveillanceEvent
from models.community.programs import (
    Indicator, VaccinationCampaign, MedicineStock, SupplyChainEvent,
    MaternalHealthRecord, ChildHealthRecord, NutritionRecord, Laboratory,
)


class CountryRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Country)


class ProvinceRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Province)

    def get_by_country(self, country_id: str) -> list:
        return self.get_by_field("country_id", country_id)


class DistrictRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, District)

    def get_by_province(self, province_id: str) -> list:
        return self.get_by_field("province_id", province_id)


class HealthFacilityRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, HealthFacility)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class HealthWorkerRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, HealthWorker)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class HealthProgramRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, HealthProgram)


class DiseaseRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Disease)


class DiseaseCaseRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, DiseaseCase)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class OutbreakRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Outbreak)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)

    def get_active(self) -> list:
        return list(self._db.query(self._model).filter(self._model.status.in_(["active", "monitoring"])).all())


class SurveillanceEventRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, SurveillanceEvent)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class IndicatorRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Indicator)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class VaccinationCampaignRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, VaccinationCampaign)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class MedicineStockRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, MedicineStock)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class SupplyChainEventRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, SupplyChainEvent)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class MaternalHealthRecordRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, MaternalHealthRecord)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class ChildHealthRecordRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, ChildHealthRecord)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class NutritionRecordRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, NutritionRecord)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)


class LaboratoryRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Laboratory)

    def get_by_district(self, district_id: str) -> list:
        return self.get_by_field("district_id", district_id)
