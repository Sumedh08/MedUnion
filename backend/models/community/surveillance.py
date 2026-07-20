from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from core.database import Base
from models.mixins import ProvenanceMixin


class Disease(ProvenanceMixin, Base):
    __tablename__ = "community_diseases"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50))
    category = Column(String(100))


class DiseaseCase(ProvenanceMixin, Base):
    __tablename__ = "community_disease_cases"

    id = Column(String(50), primary_key=True)
    disease_id = Column(String(50), nullable=True, index=True)
    district_id = Column(String(50), nullable=False, index=True)
    confirmed = Column(Integer, default=0)
    suspected = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    recovered = Column(Integer, default=0)
    reporting_week = Column(String(10))
    reported_at = Column(DateTime(timezone=True), server_default=func.now())


class Outbreak(ProvenanceMixin, Base):
    __tablename__ = "community_outbreaks"

    id = Column(String(50), primary_key=True)
    disease_id = Column(String(50), nullable=True, index=True)
    district_id = Column(String(50), nullable=False, index=True)
    status = Column(String(30))
    cases = Column(Integer, default=0)
    risk_level = Column(String(20))
    detected_at = Column(DateTime(timezone=True))
    contained_at = Column(DateTime(timezone=True), nullable=True)


class SurveillanceEvent(ProvenanceMixin, Base):
    __tablename__ = "community_surveillance_events"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), nullable=False, index=True)
    event_type = Column(String(50))
    reported_at = Column(DateTime(timezone=True))
    complete = Column(Boolean, default=False)
