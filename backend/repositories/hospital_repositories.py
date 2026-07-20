from repositories.base import BaseRepository
from models.hospital.organization import Hospital, Department, Ward, Bed
from models.hospital.clinical import Patient, Admission, Observation
from models.hospital.operations import Staff, Equipment, MedicineInventory


class HospitalRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Hospital)


class DepartmentRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Department)

    def get_by_hospital(self, hospital_id: str) -> list:
        return self.get_by_field("hospital_id", hospital_id)


class WardRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Ward)

    def get_by_department(self, department_id: str) -> list:
        return self.get_by_field("department_id", department_id)


class BedRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Bed)

    def get_by_ward(self, ward_id: str) -> list:
        return self.get_by_field("ward_id", ward_id)

    def count_by_status(self, status: str) -> int:
        return self._db.query(self._model).filter(self._model.status == status).count()


class StaffRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Staff)

    def get_by_department(self, department_id: str) -> list:
        return self.get_by_field("department_id", department_id)

    def count_active(self) -> int:
        return self._db.query(self._model).filter(self._model.active == True).count()


class EquipmentRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Equipment)

    def get_by_department(self, department_id: str) -> list:
        return self.get_by_field("department_id", department_id)

    def count_by_status(self, status: str) -> int:
        return self._db.query(self._model).filter(self._model.status == status).count()


class MedicineInventoryRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, MedicineInventory)

    def get_by_department(self, department_id: str) -> list:
        return self.get_by_field("department_id", department_id)


class PatientRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Patient)


class AdmissionRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Admission)

    def get_trend(self, days: int = 30) -> list:
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        return list(
            self._db.query(self._model)
            .filter(self._model.admitted_at >= cutoff)
            .order_by(self._model.admitted_at)
            .all()
        )
