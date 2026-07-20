from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
from models.mixins import ProvenanceMixin


class HealthFacility(ProvenanceMixin, Base):
    __tablename__ = "community_health_facilities"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), ForeignKey("community_districts.id"), nullable=False)
    name = Column(String(300), nullable=False)
    type = Column(String(50))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    district = relationship("District", back_populates="facilities")


class HealthProgram(ProvenanceMixin, Base):
    __tablename__ = "community_health_programs"

    id = Column(String(50), primary_key=True)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(30))
    budget = Column(Float, default=0)
    coverage_pct = Column(Float, default=0)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)


class HealthWorker(ProvenanceMixin, Base):
    __tablename__ = "community_health_workers"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), nullable=True)
    facility_id = Column(String(50), nullable=True)
    role = Column(String(100))
    active = Column(Boolean, default=True)
