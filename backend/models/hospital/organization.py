from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
from models.mixins import ProvenanceMixin


class Hospital(ProvenanceMixin, Base):
    __tablename__ = "hospital_hospitals"

    id = Column(String(50), primary_key=True)
    name = Column(String(300), nullable=False)
    type = Column(String(50))
    campus_count = Column(Integer, default=1)
    total_beds = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    campuses = relationship("Campus", back_populates="hospital", lazy="selectin")


class Campus(ProvenanceMixin, Base):
    __tablename__ = "hospital_campuses"

    id = Column(String(50), primary_key=True)
    hospital_id = Column(String(50), ForeignKey("hospital_hospitals.id"), nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    hospital = relationship("Hospital", back_populates="campuses")
    buildings = relationship("Building", back_populates="campus", lazy="selectin")


class Building(ProvenanceMixin, Base):
    __tablename__ = "hospital_buildings"

    id = Column(String(50), primary_key=True)
    campus_id = Column(String(50), ForeignKey("hospital_campuses.id"), nullable=False)
    name = Column(String(200), nullable=False)
    floors = Column(Integer, default=1)

    campus = relationship("Campus", back_populates="buildings")
    departments = relationship("Department", back_populates="building", lazy="selectin")


class Department(ProvenanceMixin, Base):
    __tablename__ = "hospital_departments"

    id = Column(String(50), primary_key=True)
    hospital_id = Column(String(50), ForeignKey("hospital_hospitals.id"), nullable=True)
    building_id = Column(String(50), ForeignKey("hospital_buildings.id"), nullable=True)
    name = Column(String(200), nullable=False)
    specialty = Column(String(200))
    ward_count = Column(Integer, default=1)

    building = relationship("Building", back_populates="departments")
    wards = relationship("Ward", back_populates="department", lazy="selectin")
    staff = relationship("Staff", back_populates="department", lazy="selectin")


class Ward(ProvenanceMixin, Base):
    __tablename__ = "hospital_wards"

    id = Column(String(50), primary_key=True)
    department_id = Column(String(50), ForeignKey("hospital_departments.id"), nullable=True)
    name = Column(String(255), nullable=False)
    bed_count = Column(Integer, default=0)

    department = relationship("Department", back_populates="wards")
    beds = relationship("Bed", back_populates="ward", lazy="selectin")


class Bed(ProvenanceMixin, Base):
    __tablename__ = "hospital_beds"

    id = Column(String(50), primary_key=True)
    ward_id = Column(String(50), ForeignKey("hospital_wards.id"), nullable=False)
    label = Column(String(20))
    status = Column(String(20), default="available")
    patient_id = Column(String(50), nullable=True)

    ward = relationship("Ward", back_populates="beds")
