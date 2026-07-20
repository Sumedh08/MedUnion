from repositories.hospital_repositories import (
    HospitalRepository, DepartmentRepository, WardRepository,
    BedRepository, StaffRepository, EquipmentRepository,
    MedicineInventoryRepository, PatientRepository, AdmissionRepository,
)
from repositories.community_repositories import (
    DistrictRepository, HealthFacilityRepository, HealthWorkerRepository,
    DiseaseRepository, DiseaseCaseRepository, OutbreakRepository,
    SurveillanceEventRepository, IndicatorRepository,
    VaccinationCampaignRepository, MedicineStockRepository,
)


class HospitalUnitOfWork:
    def __init__(self, db):
        self.hospitals = HospitalRepository(db)
        self.departments = DepartmentRepository(db)
        self.wards = WardRepository(db)
        self.beds = BedRepository(db)
        self.staff = StaffRepository(db)
        self.equipment = EquipmentRepository(db)
        self.inventory = MedicineInventoryRepository(db)
        self.patients = PatientRepository(db)
        self.admissions = AdmissionRepository(db)


class CommunityUnitOfWork:
    def __init__(self, db):
        self.districts = DistrictRepository(db)
        self.facilities = HealthFacilityRepository(db)
        self.health_workers = HealthWorkerRepository(db)
        self.diseases = DiseaseRepository(db)
        self.disease_cases = DiseaseCaseRepository(db)
        self.outbreaks = OutbreakRepository(db)
        self.surveillance_events = SurveillanceEventRepository(db)
        self.indicators = IndicatorRepository(db)
        self.vaccinations = VaccinationCampaignRepository(db)
        self.medicine_stock = MedicineStockRepository(db)
