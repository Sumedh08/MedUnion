from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
from models.mixins import ProvenanceMixin


class Country(ProvenanceMixin, Base):
    __tablename__ = "community_countries"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    provinces = relationship("Province", back_populates="country", lazy="selectin")


class Province(ProvenanceMixin, Base):
    __tablename__ = "community_provinces"

    id = Column(String(50), primary_key=True)
    country_id = Column(String(50), ForeignKey("community_countries.id"), nullable=False)
    name = Column(String(200), nullable=False)
    code = Column(String(10))

    country = relationship("Country", back_populates="provinces")
    counties = relationship("County", back_populates="province", lazy="selectin")


class County(ProvenanceMixin, Base):
    __tablename__ = "community_counties"

    id = Column(String(50), primary_key=True)
    province_id = Column(String(50), ForeignKey("community_provinces.id"), nullable=False)
    name = Column(String(200), nullable=False)
    code = Column(String(10))

    province = relationship("Province", back_populates="counties")
    districts = relationship("District", back_populates="county", lazy="selectin")


class District(ProvenanceMixin, Base):
    __tablename__ = "community_districts"

    id = Column(String(50), primary_key=True)
    county_id = Column(String(50), ForeignKey("community_counties.id"), nullable=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10))
    population = Column(Integer, default=0)

    county = relationship("County", back_populates="districts")
    facilities = relationship("HealthFacility", back_populates="district", lazy="selectin")
    sub_districts = relationship("SubDistrict", back_populates="district", lazy="selectin")


class SubDistrict(ProvenanceMixin, Base):
    __tablename__ = "community_sub_districts"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), ForeignKey("community_districts.id"), nullable=False)
    name = Column(String(200), nullable=False)

    district = relationship("District", back_populates="sub_districts")


class Community(ProvenanceMixin, Base):
    __tablename__ = "community_communities"

    id = Column(String(50), primary_key=True)
    district_id = Column(String(50), ForeignKey("community_districts.id"), nullable=True)
    name = Column(String(200), nullable=False)
    population = Column(Integer, default=0)
