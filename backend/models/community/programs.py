from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from core.database import Base
from models.mixins import ProvenanceMixin


class Indicator(ProvenanceMixin, Base):
    __tablename__ = "community_indicators"

    id = Column(String(50), primary_key=True)
    name = Column(String(300), nullable=False)
    value = Column(Float)
    target = Column(Float)
    district_id = Column(String(50), nullable=True)
    period = Column(String(20))
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class VaccinationCampaign(ProvenanceMixin, Base):
    __tablename__ = "community_vaccination_campaigns"

    id = Column(String(50), primary_key=True)
    vaccine = Column(String(200))
    district_id = Column(String(50), nullable=True)
    doses_target = Column(Integer, default=0)
    doses_administered = Column(Integer, default=0)
    coverage_pct = Column(Float, default=0)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30))


class MedicineStock(ProvenanceMixin, Base):
    __tablename__ = "community_medicine_stock"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), nullable=True)
    medicine = Column(String(200))
    stock_on_hand = Column(Integer, default=0)
    monthly_consumption = Column(Integer, default=0)
    days_of_stock = Column(Float, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class SupplyChainEvent(ProvenanceMixin, Base):
    __tablename__ = "community_supply_chain_events"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), nullable=True)
    medicine = Column(String(200))
    quantity = Column(Integer)
    event_type = Column(String(30))
    event_date = Column(DateTime(timezone=True))
    status = Column(String(30))


class MaternalHealthRecord(ProvenanceMixin, Base):
    __tablename__ = "community_maternal_health"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), nullable=True)
    anc_visits = Column(Integer, default=0)
    facility_deliveries = Column(Integer, default=0)
    maternal_deaths = Column(Integer, default=0)
    period = Column(String(20))
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class ChildHealthRecord(ProvenanceMixin, Base):
    __tablename__ = "community_child_health"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), nullable=True)
    under_five_population = Column(Integer, default=0)
    immunized = Column(Integer, default=0)
    malnourished = Column(Integer, default=0)
    under_five_deaths = Column(Integer, default=0)
    period = Column(String(20))
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class NutritionRecord(ProvenanceMixin, Base):
    __tablename__ = "community_nutrition"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), nullable=True)
    children_screened = Column(Integer, default=0)
    severely_malnourished = Column(Integer, default=0)
    moderately_malnourished = Column(Integer, default=0)
    receiving_supplements = Column(Integer, default=0)
    period = Column(String(20))
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class Laboratory(ProvenanceMixin, Base):
    __tablename__ = "community_laboratories"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), nullable=True)
    name = Column(String(200))
    type = Column(String(50))
    active = Column(Boolean, default=True)
    tests_per_month = Column(Integer, default=0)
    reporting_complete = Column(Boolean, default=True)
