from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from core.database import Base
from models.mixins import ProvenanceMixin


class Patient(ProvenanceMixin, Base):
    __tablename__ = "hospital_patients"

    id = Column(String(50), primary_key=True)
    age = Column(Integer)
    gender = Column(String(10))
    hospital_id = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Encounter(ProvenanceMixin, Base):
    __tablename__ = "hospital_encounters"

    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), nullable=False, index=True)
    department_id = Column(String(50), nullable=True)
    type = Column(String(30))
    start = Column(DateTime(timezone=True))
    end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Admission(ProvenanceMixin, Base):
    __tablename__ = "hospital_admissions"

    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), nullable=False, index=True)
    department_id = Column(String(50), nullable=True)
    ward_id = Column(String(50), nullable=True)
    bed_id = Column(String(50), nullable=True)
    admitted_at = Column(DateTime(timezone=True))
    discharged_at = Column(DateTime(timezone=True), nullable=True)
    diagnosis = Column(Text, nullable=True)
    outcome = Column(String(50), nullable=True)
    length_of_stay_days = Column(Float, nullable=True)


class Observation(ProvenanceMixin, Base):
    __tablename__ = "hospital_observations"

    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), nullable=False, index=True)
    encounter_id = Column(String(50), nullable=True)
    code = Column(String(100))
    value = Column(Float)
    unit = Column(String(50))
    recorded_at = Column(DateTime(timezone=True))


class MedicationAdministration(ProvenanceMixin, Base):
    __tablename__ = "hospital_medications"

    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), nullable=False, index=True)
    medicine_name = Column(String(200))
    dosage = Column(String(100))
    status = Column(String(20))
    prescribed_at = Column(DateTime(timezone=True))
    administered_at = Column(DateTime(timezone=True), nullable=True)


class LaboratoryResult(ProvenanceMixin, Base):
    __tablename__ = "hospital_lab_results"

    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), nullable=False, index=True)
    encounter_id = Column(String(50), nullable=True)
    test_name = Column(String(200))
    test_category = Column(String(100))
    result_value = Column(String(200))
    result_unit = Column(String(50))
    reference_range = Column(String(100), nullable=True)
    is_abnormal = Column(Integer, default=0)
    performed_at = Column(DateTime(timezone=True))
    turnaround_hours = Column(Float, nullable=True)


class ImagingStudy(ProvenanceMixin, Base):
    __tablename__ = "hospital_imaging_studies"

    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), nullable=False, index=True)
    study_type = Column(String(100))
    body_site = Column(String(100))
    status = Column(String(30))
    ordered_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    turnaround_hours = Column(Float, nullable=True)


class Procedure(ProvenanceMixin, Base):
    __tablename__ = "hospital_procedures"

    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), nullable=False, index=True)
    procedure_type = Column(String(200))
    department_id = Column(String(50), nullable=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30))
