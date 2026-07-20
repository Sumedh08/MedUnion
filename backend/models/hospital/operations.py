from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
from models.mixins import ProvenanceMixin


class Staff(ProvenanceMixin, Base):
    __tablename__ = "hospital_staff"

    id = Column(String(50), primary_key=True)
    department_id = Column(String(50), ForeignKey("hospital_departments.id"), nullable=True)
    name = Column(String(200))
    role = Column(String(100))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    department = relationship("Department", back_populates="staff", lazy="selectin")


class Shift(ProvenanceMixin, Base):
    __tablename__ = "hospital_shifts"

    id = Column(String(50), primary_key=True)
    staff_id = Column(String(50), nullable=False, index=True)
    department_id = Column(String(50), nullable=True)
    start = Column(DateTime(timezone=True))
    end = Column(DateTime(timezone=True), nullable=True)
    shift_type = Column(String(30))


class Equipment(ProvenanceMixin, Base):
    __tablename__ = "hospital_equipment"

    id = Column(String(50), primary_key=True)
    department_id = Column(String(50), nullable=True)
    equipment_type = Column(String(100))
    status = Column(String(30))
    last_maintenance = Column(DateTime(timezone=True), nullable=True)
    next_maintenance = Column(DateTime(timezone=True), nullable=True)


class OperatingRoom(ProvenanceMixin, Base):
    __tablename__ = "hospital_operating_rooms"

    id = Column(String(50), primary_key=True)
    department_id = Column(String(50), nullable=True)
    name = Column(String(100))
    status = Column(String(30))
    current_procedure_id = Column(String(50), nullable=True)
    scheduled_start = Column(DateTime(timezone=True), nullable=True)
    scheduled_end = Column(DateTime(timezone=True), nullable=True)


class EmergencyVisit(ProvenanceMixin, Base):
    __tablename__ = "hospital_emergency_visits"

    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), nullable=False, index=True)
    acuity = Column(Integer)
    chief_complaint = Column(String(300))
    arrival_time = Column(DateTime(timezone=True))
    triage_time = Column(DateTime(timezone=True), nullable=True)
    seen_by_doctor = Column(DateTime(timezone=True), nullable=True)
    disposition = Column(String(50), nullable=True)
    disposition_time = Column(DateTime(timezone=True), nullable=True)
    wait_time_minutes = Column(Integer, nullable=True)


class Appointment(ProvenanceMixin, Base):
    __tablename__ = "hospital_appointments"

    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), nullable=False, index=True)
    department_id = Column(String(50), nullable=True)
    scheduled_at = Column(DateTime(timezone=True))
    status = Column(String(30))
    reason = Column(String(300), nullable=True)


class MedicineInventory(ProvenanceMixin, Base):
    __tablename__ = "hospital_medicine_inventory"

    id = Column(String(50), primary_key=True)
    department_id = Column(String(50), nullable=True)
    medicine_name = Column(String(200))
    stock_current = Column(Float)
    stock_max = Column(Float)
    consumption_rate = Column(Float)
    days_until_stockout = Column(Float)
    unit = Column(String(20), default="units")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
