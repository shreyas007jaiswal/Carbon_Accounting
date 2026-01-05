"""
Carbon Accounting API - Master Tables and Scope 1 Subtables
FastAPI application with SQLAlchemy ORM for carbon emissions tracking.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================

DATABASE_URL = "sqlite:///./carbon_accounting.db"  # Change for production
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# ENUMS
# ==============================================================================

class UserRole(str, Enum):
    MANAGER = "Manager"
    ANALYST = "Analyst"
    EMPLOYEE = "Employee"
    SUPPLIER = "Supplier"


class FacilityType(str, Enum):
    OFFICE = "office"
    PLANT = "plant"
    WAREHOUSE = "warehouse"


class ScopeType(int, Enum):
    SCOPE_1 = 1
    SCOPE_2 = 2
    SCOPE_3 = 3


class EmissionCategory(str, Enum):
    FUEL_COMBUSTION = "Fuel Combustion"
    ENERGY = "Energy"
    ELECTRICITY = "Electricity"
    PROCUREMENT = "Procurement"
    TRAVEL = "Travel"
    WASTE = "Waste"
    TRANSPORT = "Transport"
    REFRIGERANT = "Refrigerant"
    PROCESS = "Process"


# ==============================================================================
# MASTER TABLES - SQLAlchemy Models
# ==============================================================================

class Organization(Base):
    """Organization master table - stores company-level info."""
    __tablename__ = "organization"

    organization_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    country = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
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

    # Relationships
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

    # Relationships
    organization = relationship("Organization", back_populates="facilities")
    emission_activities = relationship("EmissionActivity", back_populates="facility", cascade="all, delete-orphan")


class Supplier(Base):
    """Supplier table - procurement partners for Scope 3."""
    __tablename__ = "supplier"

    supplier_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255))  # Procurement category (steel, plastic, logistics)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    emission_activities = relationship("EmissionActivity", back_populates="supplier")


class EmissionFactor(Base):
    """Emission Factor table - holds factors to convert activity data to CO₂e."""
    __tablename__ = "emission_factor"

    factor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(100), nullable=False)  # Fuel, Electricity, Travel, etc.
    region = Column(String(100))
    unit = Column(String(100))  # kg CO₂e/kWh, kg CO₂e/liter, etc.
    value = Column(DECIMAL(18, 6), nullable=False)
    valid_from = Column(Date)
    valid_to = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    stationary_fuels = relationship("StationaryFuel", back_populates="emission_factor")
    company_vehicles = relationship("CompanyVehicle", back_populates="emission_factor")
    refrigerant_leaks = relationship("RefrigerantLeak", back_populates="emission_factor")
    process_emissions = relationship("ProcessEmission", back_populates="emission_factor")


# ==============================================================================
# ACTIVITY & SCOPE 1 SUBTABLES - SQLAlchemy Models
# ==============================================================================

class EmissionActivity(Base):
    """Emission Activity table - generic parent table for all emission activities."""
    __tablename__ = "emission_activity"

    activity_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.organization_id", ondelete="CASCADE"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facility.facility_id", ondelete="SET NULL"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("supplier.supplier_id", ondelete="SET NULL"), nullable=True)
    scope = Column(Integer, nullable=False)  # 1, 2, or 3
    category = Column(String(100), nullable=False)
    activity_date = Column(Date, nullable=False)
    quantity = Column(DECIMAL(18, 4))
    unit = Column(String(50))
    source_reference = Column(String(255))  # Invoice, survey, log, API
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="emission_activities")
    facility = relationship("Facility", back_populates="emission_activities")
    supplier = relationship("Supplier", back_populates="emission_activities")
    calculations = relationship("EmissionCalculation", back_populates="activity", cascade="all, delete-orphan")
    
    # Scope 1 subtable relationships
    stationary_fuels = relationship("StationaryFuel", back_populates="activity", cascade="all, delete-orphan")
    company_vehicles = relationship("CompanyVehicle", back_populates="activity", cascade="all, delete-orphan")
    refrigerant_leaks = relationship("RefrigerantLeak", back_populates="activity", cascade="all, delete-orphan")
    process_emissions = relationship("ProcessEmission", back_populates="activity", cascade="all, delete-orphan")


class EmissionCalculation(Base):
    """Emission Calculation table - CO₂e results from activity × emission factor."""
    __tablename__ = "emission_calculation"

    calculation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    co2e_value = Column(DECIMAL(18, 4), nullable=False)  # Tons of CO₂e
    calculation_method = Column(String(100))  # Factor / spend-based etc.
    factor_used = Column(String(255))
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    activity = relationship("EmissionActivity", back_populates="calculations")


# ------------------------------------------------------------------------------
# SCOPE 1 SUBTABLES
# ------------------------------------------------------------------------------

class StationaryFuel(Base):
    """Stationary Fuel - Scope 1 subtable for stationary combustion sources."""
    __tablename__ = "stationary_fuel"

    fuel_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    fuel_type = Column(String(100), nullable=False)  # Natural gas, diesel, coal, etc.
    quantity = Column(DECIMAL(18, 4), nullable=False)
    unit = Column(String(50), nullable=False)  # liters, kg, cubic meters, etc.
    factor_id = Column(Integer, ForeignKey("emission_factor.factor_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    activity = relationship("EmissionActivity", back_populates="stationary_fuels")
    emission_factor = relationship("EmissionFactor", back_populates="stationary_fuels")


class CompanyVehicle(Base):
    """Company Vehicle - Scope 1 subtable for mobile combustion (company-owned vehicles)."""
    __tablename__ = "company_vehicle"

    vehicle_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    vehicle_type = Column(String(100), nullable=False)  # Car, truck, van, etc.
    distance_travelled = Column(DECIMAL(18, 4))  # km or miles
    fuel_consumed = Column(DECIMAL(18, 4))  # liters or gallons
    factor_id = Column(Integer, ForeignKey("emission_factor.factor_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    activity = relationship("EmissionActivity", back_populates="company_vehicles")
    emission_factor = relationship("EmissionFactor", back_populates="company_vehicles")


class RefrigerantLeak(Base):
    """Refrigerant Leak - Scope 1 subtable for fugitive emissions from refrigerants."""
    __tablename__ = "refrigerant_leak"

    refrigerant_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    refrigerant_type = Column(String(100), nullable=False)  # R-134a, R-410A, etc.
    leak_quantity_kg = Column(DECIMAL(18, 4), nullable=False)
    gwp_factor = Column(DECIMAL(18, 4))  # Global Warming Potential
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
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

    # Relationships
    activity = relationship("EmissionActivity", back_populates="process_emissions")
    emission_factor = relationship("EmissionFactor", back_populates="process_emissions")


# ==============================================================================
# PYDANTIC SCHEMAS - Request/Response Models
# ==============================================================================

# --- Organization Schemas ---
class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=255)
    sector: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- User Schemas ---
class UserBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: str = Field(..., max_length=255)
    role: Optional[str] = Field(UserRole.EMPLOYEE.value, max_length=50)


class UserCreate(UserBase):
    organization_id: int


class UserResponse(UserBase):
    user_id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Facility Schemas ---
class FacilityBase(BaseModel):
    name: str = Field(..., max_length=255)
    location_region: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=50)


class FacilityCreate(FacilityBase):
    organization_id: int


class FacilityResponse(FacilityBase):
    facility_id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Supplier Schemas ---
class SupplierBase(BaseModel):
    name: str = Field(..., max_length=255)
    category: Optional[str] = Field(None, max_length=255)


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    supplier_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Emission Factor Schemas ---
class EmissionFactorBase(BaseModel):
    category: str = Field(..., max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=100)
    value: Decimal
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


class EmissionFactorCreate(EmissionFactorBase):
    pass


class EmissionFactorResponse(EmissionFactorBase):
    factor_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Emission Activity Schemas ---
class EmissionActivityBase(BaseModel):
    scope: int = Field(..., ge=1, le=3)
    category: str = Field(..., max_length=100)
    activity_date: date
    quantity: Optional[Decimal] = None
    unit: Optional[str] = Field(None, max_length=50)
    source_reference: Optional[str] = Field(None, max_length=255)


class EmissionActivityCreate(EmissionActivityBase):
    organization_id: int
    facility_id: Optional[int] = None
    supplier_id: Optional[int] = None


class EmissionActivityResponse(EmissionActivityBase):
    activity_id: int
    organization_id: int
    facility_id: Optional[int]
    supplier_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Emission Calculation Schemas ---
class EmissionCalculationBase(BaseModel):
    co2e_value: Decimal
    calculation_method: Optional[str] = Field(None, max_length=100)
    factor_used: Optional[str] = Field(None, max_length=255)


class EmissionCalculationCreate(EmissionCalculationBase):
    activity_id: int


class EmissionCalculationResponse(EmissionCalculationBase):
    calculation_id: int
    activity_id: int
    calculated_at: datetime

    class Config:
        from_attributes = True


# --- Scope 1: Stationary Fuel Schemas ---
class StationaryFuelBase(BaseModel):
    fuel_type: str = Field(..., max_length=100)
    quantity: Decimal
    unit: str = Field(..., max_length=50)
    factor_id: Optional[int] = None


class StationaryFuelCreate(StationaryFuelBase):
    activity_id: int


class StationaryFuelResponse(StationaryFuelBase):
    fuel_id: int
    activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Scope 1: Company Vehicle Schemas ---
class CompanyVehicleBase(BaseModel):
    vehicle_type: str = Field(..., max_length=100)
    distance_travelled: Optional[Decimal] = None
    fuel_consumed: Optional[Decimal] = None
    factor_id: Optional[int] = None


class CompanyVehicleCreate(CompanyVehicleBase):
    activity_id: int


class CompanyVehicleResponse(CompanyVehicleBase):
    vehicle_id: int
    activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Scope 1: Refrigerant Leak Schemas ---
class RefrigerantLeakBase(BaseModel):
    refrigerant_type: str = Field(..., max_length=100)
    leak_quantity_kg: Decimal
    gwp_factor: Optional[Decimal] = None


class RefrigerantLeakCreate(RefrigerantLeakBase):
    activity_id: int


class RefrigerantLeakResponse(RefrigerantLeakBase):
    refrigerant_id: int
    activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Scope 1: Process Emission Schemas ---
class ProcessEmissionBase(BaseModel):
    material_type: str = Field(..., max_length=100)
    quantity_processed: Decimal
    factor_id: Optional[int] = None


class ProcessEmissionCreate(ProcessEmissionBase):
    activity_id: int


class ProcessEmissionResponse(ProcessEmissionBase):
    process_id: int
    activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# FASTAPI APPLICATION
# ==============================================================================

app = FastAPI(
    title="Carbon Accounting API",
    description="API for tracking Scope 1, 2, and 3 emissions with master tables and Scope 1 subtables.",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


# ==============================================================================
# API ENDPOINTS - Master Tables
# ==============================================================================

# --- Organization Endpoints ---
@app.post("/organizations/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED, tags=["Organizations"])
def create_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    """Create a new organization."""
    db_org = Organization(**org.model_dump())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org


@app.get("/organizations/", response_model=List[OrganizationResponse], tags=["Organizations"])
def get_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all organizations."""
    return db.query(Organization).offset(skip).limit(limit).all()


@app.get("/organizations/{organization_id}", response_model=OrganizationResponse, tags=["Organizations"])
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific organization by ID."""
    org = db.query(Organization).filter(Organization.organization_id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@app.delete("/organizations/{organization_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Organizations"])
def delete_organization(organization_id: int, db: Session = Depends(get_db)):
    """Delete an organization (cascades to related records)."""
    org = db.query(Organization).filter(Organization.organization_id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    db.delete(org)
    db.commit()


# --- User Endpoints ---
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Verify organization exists
    org = db.query(Organization).filter(Organization.organization_id == user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[UserResponse], tags=["Users"])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all users."""
    return db.query(User).offset(skip).limit(limit).all()


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific user by ID."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# --- Facility Endpoints ---
@app.post("/facilities/", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED, tags=["Facilities"])
def create_facility(facility: FacilityCreate, db: Session = Depends(get_db)):
    """Create a new facility."""
    org = db.query(Organization).filter(Organization.organization_id == facility.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    db_facility = Facility(**facility.model_dump())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility


@app.get("/facilities/", response_model=List[FacilityResponse], tags=["Facilities"])
def get_facilities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all facilities."""
    return db.query(Facility).offset(skip).limit(limit).all()


@app.get("/facilities/{facility_id}", response_model=FacilityResponse, tags=["Facilities"])
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific facility by ID."""
    facility = db.query(Facility).filter(Facility.facility_id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility


# --- Supplier Endpoints ---
@app.post("/suppliers/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED, tags=["Suppliers"])
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    """Create a new supplier."""
    db_supplier = Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


@app.get("/suppliers/", response_model=List[SupplierResponse], tags=["Suppliers"])
def get_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all suppliers."""
    return db.query(Supplier).offset(skip).limit(limit).all()


@app.get("/suppliers/{supplier_id}", response_model=SupplierResponse, tags=["Suppliers"])
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific supplier by ID."""
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


# --- Emission Factor Endpoints ---
@app.post("/emission-factors/", response_model=EmissionFactorResponse, status_code=status.HTTP_201_CREATED, tags=["Emission Factors"])
def create_emission_factor(factor: EmissionFactorCreate, db: Session = Depends(get_db)):
    """Create a new emission factor."""
    db_factor = EmissionFactor(**factor.model_dump())
    db.add(db_factor)
    db.commit()
    db.refresh(db_factor)
    return db_factor


@app.get("/emission-factors/", response_model=List[EmissionFactorResponse], tags=["Emission Factors"])
def get_emission_factors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all emission factors."""
    return db.query(EmissionFactor).offset(skip).limit(limit).all()


@app.get("/emission-factors/{factor_id}", response_model=EmissionFactorResponse, tags=["Emission Factors"])
def get_emission_factor(factor_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific emission factor by ID."""
    factor = db.query(EmissionFactor).filter(EmissionFactor.factor_id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Emission factor not found")
    return factor


# ==============================================================================
# API ENDPOINTS - Emission Activity & Calculation
# ==============================================================================

@app.post("/emission-activities/", response_model=EmissionActivityResponse, status_code=status.HTTP_201_CREATED, tags=["Emission Activities"])
def create_emission_activity(activity: EmissionActivityCreate, db: Session = Depends(get_db)):
    """Create a new emission activity."""
    # Verify organization exists
    org = db.query(Organization).filter(Organization.organization_id == activity.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Verify facility if provided
    if activity.facility_id:
        facility = db.query(Facility).filter(Facility.facility_id == activity.facility_id).first()
        if not facility:
            raise HTTPException(status_code=404, detail="Facility not found")
    
    # Verify supplier if provided
    if activity.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.supplier_id == activity.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
    
    db_activity = EmissionActivity(**activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


@app.get("/emission-activities/", response_model=List[EmissionActivityResponse], tags=["Emission Activities"])
def get_emission_activities(
    scope: Optional[int] = None,
    organization_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve emission activities with optional filters."""
    query = db.query(EmissionActivity)
    if scope:
        query = query.filter(EmissionActivity.scope == scope)
    if organization_id:
        query = query.filter(EmissionActivity.organization_id == organization_id)
    return query.offset(skip).limit(limit).all()


@app.get("/emission-activities/{activity_id}", response_model=EmissionActivityResponse, tags=["Emission Activities"])
def get_emission_activity(activity_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific emission activity by ID."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    return activity


@app.delete("/emission-activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Emission Activities"])
def delete_emission_activity(activity_id: int, db: Session = Depends(get_db)):
    """Delete an emission activity (cascades to related Scope 1/2/3 and calculation records)."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    db.delete(activity)
    db.commit()


# --- Emission Calculation Endpoints ---
@app.post("/emission-calculations/", response_model=EmissionCalculationResponse, status_code=status.HTTP_201_CREATED, tags=["Emission Calculations"])
def create_emission_calculation(calculation: EmissionCalculationCreate, db: Session = Depends(get_db)):
    """Create a new emission calculation."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == calculation.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    db_calc = EmissionCalculation(**calculation.model_dump())
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc


@app.get("/emission-calculations/", response_model=List[EmissionCalculationResponse], tags=["Emission Calculations"])
def get_emission_calculations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all emission calculations."""
    return db.query(EmissionCalculation).offset(skip).limit(limit).all()


# ==============================================================================
# API ENDPOINTS - Scope 1 Subtables
# ==============================================================================

# --- Stationary Fuel Endpoints ---
@app.post("/scope1/stationary-fuels/", response_model=StationaryFuelResponse, status_code=status.HTTP_201_CREATED, tags=["Scope 1 - Stationary Fuel"])
def create_stationary_fuel(fuel: StationaryFuelCreate, db: Session = Depends(get_db)):
    """Create a new stationary fuel record."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == fuel.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    if fuel.factor_id:
        factor = db.query(EmissionFactor).filter(EmissionFactor.factor_id == fuel.factor_id).first()
        if not factor:
            raise HTTPException(status_code=404, detail="Emission factor not found")
    
    db_fuel = StationaryFuel(**fuel.model_dump())
    db.add(db_fuel)
    db.commit()
    db.refresh(db_fuel)
    return db_fuel


@app.get("/scope1/stationary-fuels/", response_model=List[StationaryFuelResponse], tags=["Scope 1 - Stationary Fuel"])
def get_stationary_fuels(activity_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve stationary fuel records."""
    query = db.query(StationaryFuel)
    if activity_id:
        query = query.filter(StationaryFuel.activity_id == activity_id)
    return query.offset(skip).limit(limit).all()


@app.get("/scope1/stationary-fuels/{fuel_id}", response_model=StationaryFuelResponse, tags=["Scope 1 - Stationary Fuel"])
def get_stationary_fuel(fuel_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific stationary fuel record."""
    fuel = db.query(StationaryFuel).filter(StationaryFuel.fuel_id == fuel_id).first()
    if not fuel:
        raise HTTPException(status_code=404, detail="Stationary fuel not found")
    return fuel


# --- Company Vehicle Endpoints ---
@app.post("/scope1/company-vehicles/", response_model=CompanyVehicleResponse, status_code=status.HTTP_201_CREATED, tags=["Scope 1 - Company Vehicles"])
def create_company_vehicle(vehicle: CompanyVehicleCreate, db: Session = Depends(get_db)):
    """Create a new company vehicle record."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == vehicle.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    if vehicle.factor_id:
        factor = db.query(EmissionFactor).filter(EmissionFactor.factor_id == vehicle.factor_id).first()
        if not factor:
            raise HTTPException(status_code=404, detail="Emission factor not found")
    
    db_vehicle = CompanyVehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@app.get("/scope1/company-vehicles/", response_model=List[CompanyVehicleResponse], tags=["Scope 1 - Company Vehicles"])
def get_company_vehicles(activity_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve company vehicle records."""
    query = db.query(CompanyVehicle)
    if activity_id:
        query = query.filter(CompanyVehicle.activity_id == activity_id)
    return query.offset(skip).limit(limit).all()


@app.get("/scope1/company-vehicles/{vehicle_id}", response_model=CompanyVehicleResponse, tags=["Scope 1 - Company Vehicles"])
def get_company_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific company vehicle record."""
    vehicle = db.query(CompanyVehicle).filter(CompanyVehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Company vehicle not found")
    return vehicle


# --- Refrigerant Leak Endpoints ---
@app.post("/scope1/refrigerant-leaks/", response_model=RefrigerantLeakResponse, status_code=status.HTTP_201_CREATED, tags=["Scope 1 - Refrigerant Leaks"])
def create_refrigerant_leak(leak: RefrigerantLeakCreate, db: Session = Depends(get_db)):
    """Create a new refrigerant leak record."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == leak.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    db_leak = RefrigerantLeak(**leak.model_dump())
    db.add(db_leak)
    db.commit()
    db.refresh(db_leak)
    return db_leak


@app.get("/scope1/refrigerant-leaks/", response_model=List[RefrigerantLeakResponse], tags=["Scope 1 - Refrigerant Leaks"])
def get_refrigerant_leaks(activity_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve refrigerant leak records."""
    query = db.query(RefrigerantLeak)
    if activity_id:
        query = query.filter(RefrigerantLeak.activity_id == activity_id)
    return query.offset(skip).limit(limit).all()


@app.get("/scope1/refrigerant-leaks/{refrigerant_id}", response_model=RefrigerantLeakResponse, tags=["Scope 1 - Refrigerant Leaks"])
def get_refrigerant_leak(refrigerant_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific refrigerant leak record."""
    leak = db.query(RefrigerantLeak).filter(RefrigerantLeak.refrigerant_id == refrigerant_id).first()
    if not leak:
        raise HTTPException(status_code=404, detail="Refrigerant leak not found")
    return leak


# --- Process Emission Endpoints ---
@app.post("/scope1/process-emissions/", response_model=ProcessEmissionResponse, status_code=status.HTTP_201_CREATED, tags=["Scope 1 - Process Emissions"])
def create_process_emission(process: ProcessEmissionCreate, db: Session = Depends(get_db)):
    """Create a new process emission record."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == process.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    if process.factor_id:
        factor = db.query(EmissionFactor).filter(EmissionFactor.factor_id == process.factor_id).first()
        if not factor:
            raise HTTPException(status_code=404, detail="Emission factor not found")
    
    db_process = ProcessEmission(**process.model_dump())
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    return db_process


@app.get("/scope1/process-emissions/", response_model=List[ProcessEmissionResponse], tags=["Scope 1 - Process Emissions"])
def get_process_emissions(activity_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve process emission records."""
    query = db.query(ProcessEmission)
    if activity_id:
        query = query.filter(ProcessEmission.activity_id == activity_id)
    return query.offset(skip).limit(limit).all()


@app.get("/scope1/process-emissions/{process_id}", response_model=ProcessEmissionResponse, tags=["Scope 1 - Process Emissions"])
def get_process_emission(process_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific process emission record."""
    process = db.query(ProcessEmission).filter(ProcessEmission.process_id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Process emission not found")
    return process


# ==============================================================================
# HEALTH CHECK
# ==============================================================================

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)