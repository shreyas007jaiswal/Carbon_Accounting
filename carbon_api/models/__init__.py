"""
Models Package
SQLAlchemy ORM models for all database tables.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from ..database import Base
from ..enums import UserRole


# ==============================================================================
# MASTER TABLES
# ==============================================================================

class Organization(Base):
    """Organization master table - stores company-level info."""
    __tablename__ = "organization"

    organization_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    country = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    facilities = relationship("Facility", back_populates="organization", cascade="all, delete-orphan")
    emission_activities = relationship("EmissionActivity", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    """User table - stores users belonging to organizations."""
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.organization_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(50), default=UserRole.EMPLOYEE.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")


class Facility(Base):
    """Facility table - represents sites/plants where emissions occur."""
    __tablename__ = "facility"

    facility_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.organization_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    location_region = Column(String(255))
    type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="facilities")
    emission_activities = relationship("EmissionActivity", back_populates="facility", cascade="all, delete-orphan")


class Supplier(Base):
    """Supplier table - procurement partners for Scope 3."""
    __tablename__ = "supplier"

    supplier_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    emission_activities = relationship("EmissionActivity", back_populates="supplier")


class EmissionFactor(Base):
    """Emission Factor table - holds factors to convert activity data to CO₂e."""
    __tablename__ = "emission_factor"

    factor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    region = Column(String(100))
    unit = Column(String(100))
    value = Column(DECIMAL(18, 6), nullable=False)
    valid_from = Column(Date)
    valid_to = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    stationary_fuels = relationship("StationaryFuel", back_populates="emission_factor")
    company_vehicles = relationship("CompanyVehicle", back_populates="emission_factor")
    refrigerant_leaks = relationship("RefrigerantLeak", back_populates="emission_factor")
    process_emissions = relationship("ProcessEmission", back_populates="emission_factor")


# ==============================================================================
# ACTIVITY & CALCULATION TABLES
# ==============================================================================

class EmissionActivity(Base):
    """Emission Activity table - generic parent table for all emission activities."""
    __tablename__ = "emission_activity"

    activity_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.organization_id", ondelete="CASCADE"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facility.facility_id", ondelete="SET NULL"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("supplier.supplier_id", ondelete="SET NULL"), nullable=True)
    scope = Column(Integer, nullable=False)
    category = Column(String(100), nullable=False)
    activity_date = Column(Date, nullable=False)
    quantity = Column(DECIMAL(18, 4))
    unit = Column(String(50))
    source_reference = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="emission_activities")
    facility = relationship("Facility", back_populates="emission_activities")
    supplier = relationship("Supplier", back_populates="emission_activities")
    calculations = relationship("EmissionCalculation", back_populates="activity", cascade="all, delete-orphan")
    stationary_fuels = relationship("StationaryFuel", back_populates="activity", cascade="all, delete-orphan")
    company_vehicles = relationship("CompanyVehicle", back_populates="activity", cascade="all, delete-orphan")
    refrigerant_leaks = relationship("RefrigerantLeak", back_populates="activity", cascade="all, delete-orphan")
    process_emissions = relationship("ProcessEmission", back_populates="activity", cascade="all, delete-orphan")


class EmissionCalculation(Base):
    """Emission Calculation table - CO₂e results from activity × emission factor."""
    __tablename__ = "emission_calculation"

    calculation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    co2e_value = Column(DECIMAL(18, 4), nullable=False)
    calculation_method = Column(String(100))
    factor_used = Column(String(255))
    calculated_at = Column(DateTime, default=datetime.utcnow)

    activity = relationship("EmissionActivity", back_populates="calculations")


# ==============================================================================
# SCOPE 1 SUBTABLES
# ==============================================================================

class StationaryFuel(Base):
    """Stationary Fuel - Scope 1 subtable for stationary combustion sources."""
    __tablename__ = "stationary_fuel"

    fuel_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    fuel_type = Column(String(100), nullable=False)
    quantity = Column(DECIMAL(18, 4), nullable=False)
    unit = Column(String(50), nullable=False)
    factor_id = Column(Integer, ForeignKey("emission_factor.factor_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    activity = relationship("EmissionActivity", back_populates="stationary_fuels")
    emission_factor = relationship("EmissionFactor", back_populates="stationary_fuels")


class CompanyVehicle(Base):
    """Company Vehicle - Scope 1 subtable for mobile combustion."""
    __tablename__ = "company_vehicle"

    vehicle_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    vehicle_type = Column(String(100), nullable=False)
    distance_travelled = Column(DECIMAL(18, 4))
    fuel_consumed = Column(DECIMAL(18, 4))
    factor_id = Column(Integer, ForeignKey("emission_factor.factor_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    activity = relationship("EmissionActivity", back_populates="company_vehicles")
    emission_factor = relationship("EmissionFactor", back_populates="company_vehicles")


class RefrigerantLeak(Base):
    """Refrigerant Leak - Scope 1 subtable for fugitive emissions."""
    __tablename__ = "refrigerant_leak"

    refrigerant_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    refrigerant_type = Column(String(100), nullable=False)
    leak_quantity_kg = Column(DECIMAL(18, 4), nullable=False)
    gwp_factor = Column(DECIMAL(18, 4))
    created_at = Column(DateTime, default=datetime.utcnow)

    activity = relationship("EmissionActivity", back_populates="refrigerant_leaks")


class ProcessEmission(Base):
    """Process Emission - Scope 1 subtable for industrial process emissions."""
    __tablename__ = "process_emission"

    process_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    material_type = Column(String(100), nullable=False)
    quantity_processed = Column(DECIMAL(18, 4), nullable=False)
    factor_id = Column(Integer, ForeignKey("emission_factor.factor_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    activity = relationship("EmissionActivity", back_populates="process_emissions")
    emission_factor = relationship("EmissionFactor", back_populates="process_emissions")


__all__ = [
    "Organization",
    "User",
    "Facility",
    "Supplier",
    "EmissionFactor",
    "EmissionActivity",
    "EmissionCalculation",
    "StationaryFuel",
    "CompanyVehicle",
    "RefrigerantLeak",
    "ProcessEmission",
]
