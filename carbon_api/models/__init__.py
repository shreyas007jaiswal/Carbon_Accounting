"""
Models Package
SQLAlchemy ORM models for all database tables.
Includes:
- Master Tables (Organization, User, Facility, Supplier)
- RBAC Tables (Role, Permission, RolePermission, UserRole)
- Field Security Tables (ResourceField, FieldPermission)
- ABAC Tables (Policy, RolePolicy)
- Audit Tables (AuthorizationAudit)
- Emission Tables (EmissionActivity, EmissionCalculation, Scope 1 subtables)
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
    Boolean,
    Text,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from ..database import Base
from ..enums import RoleScope, Action, UserStatus, OrganizationStatus


# ==============================================================================
# MASTER TABLES (Identity & Tenant)
# ==============================================================================

class Organization(Base):
    """Organization master table - tenant in multi-tenant SaaS."""
    __tablename__ = "organization"

    organization_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    country = Column(String(100))
    status = Column(String(50), default=OrganizationStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    facilities = relationship("Facility", back_populates="organization", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="organization", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="organization", cascade="all, delete-orphan")
    emission_activities = relationship("EmissionActivity", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    """User table - users belonging to organizations."""
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.organization_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), default=UserStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")


class Facility(Base):
    """Facility table - sites/plants where emissions occur."""
    __tablename__ = "facility"

    facility_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.organization_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(255))  # Renamed from location_region for consistency with doc
    type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="facilities")
    user_roles = relationship("UserRole", back_populates="facility")
    emission_activities = relationship("EmissionActivity", back_populates="facility", cascade="all, delete-orphan")


class Supplier(Base):
    """Supplier table - procurement partners for Scope 3."""
    __tablename__ = "supplier"

    supplier_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.organization_id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    procurement_category = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    emission_activities = relationship("EmissionActivity", back_populates="supplier")



# ==============================================================================
# ADDITIONAL MASTER TABLES (Reference Data)
# ==============================================================================

class FuelType(Base):
    """Fuel Type master table - used by StationaryFuel."""
    __tablename__ = "fuel_type"

    fuel_type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Scope(Base):
    """Scope master table - reference for Scope 1/2/3."""
    __tablename__ = "scope"

    scope_id = Column(Integer, primary_key=True, index=True, autoincrement=False)  # 1,2,3
    scope_label = Column(String(50), nullable=False, unique=True)  # 'Scope 1', etc.


class Unit(Base):
    """Unit master table - reference list of units."""
    __tablename__ = "unit"

    unit_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    unit = Column(String(50), nullable=False, unique=True)


class Sector(Base):
    """Sector master table - reference list of sectors."""
    __tablename__ = "sector"

    sector_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sector = Column(String(100), nullable=False, unique=True)


# ==============================================================================
# RBAC TABLES (Role-Based Access Control)
# ==============================================================================

class Role(Base):
    """Role table - customer-defined roles scoped to ORG or FACILITY."""
    __tablename__ = "role"

    role_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.organization_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    scope = Column(String(20), nullable=False)  # 'ORG' or 'FACILITY'
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    field_permissions = relationship("FieldPermission", back_populates="role", cascade="all, delete-orphan")
    role_policies = relationship("RolePolicy", back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    """Permission table - atomic actions on resources (CRUD)."""
    __tablename__ = "permission"

    permission_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resource = Column(String(100), nullable=False)  # EMISSION, REPORT, FACILITY, etc.
    action = Column(String(20), nullable=False)  # CREATE, READ, UPDATE, DELETE
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),
    )

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class RolePermission(Base):
    """RolePermission table - maps roles to permissions (RBAC core)."""
    __tablename__ = "role_permission"

    role_id = Column(Integer, ForeignKey("role.role_id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permission.permission_id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")


class UserRole(Base):
    """UserRole table - assigns roles to users with optional facility scoping."""
    __tablename__ = "user_role"

    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("role.role_id", ondelete="CASCADE"), primary_key=True)
    facility_id = Column(Integer, ForeignKey("facility.facility_id", ondelete="CASCADE"), primary_key=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    facility = relationship("Facility", back_populates="user_roles")


# ==============================================================================
# FIELD-LEVEL SECURITY TABLES
# ==============================================================================

class ResourceField(Base):
    """ResourceField table - registry of fields for each resource."""
    __tablename__ = "resource_field"

    field_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resource = Column(String(100), nullable=False)  # EMISSION, REPORT, etc.
    field_name = Column(String(100), nullable=False)  # quantity, emission_factor, co2e, etc.
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('resource', 'field_name', name='uq_resource_field'),
    )

    # Relationships
    field_permissions = relationship("FieldPermission", back_populates="resource_field", cascade="all, delete-orphan")


class FieldPermission(Base):
    """FieldPermission table - controls field read/update access per role."""
    __tablename__ = "field_permission"

    role_id = Column(Integer, ForeignKey("role.role_id", ondelete="CASCADE"), primary_key=True)
    field_id = Column(Integer, ForeignKey("resource_field.field_id", ondelete="CASCADE"), primary_key=True)
    can_read = Column(Boolean, default=False)
    can_update = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    role = relationship("Role", back_populates="field_permissions")
    resource_field = relationship("ResourceField", back_populates="field_permissions")


# ==============================================================================
# ABAC TABLES (Attribute-Based Access Control)
# ==============================================================================

class Policy(Base):
    """Policy table - ABAC policies with JSON conditions."""
    __tablename__ = "policy"

    policy_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.organization_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100))
    resource = Column(String(100), nullable=False)  # EMISSION, REPORT, etc.
    action = Column(String(20), nullable=False)  # CREATE, READ, UPDATE, DELETE
    conditions = Column(JSON, nullable=False)  # JSON conditions for evaluation
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="policies")
    role_policies = relationship("RolePolicy", back_populates="policy", cascade="all, delete-orphan")


class RolePolicy(Base):
    """RolePolicy table - maps roles to policies."""
    __tablename__ = "role_policy"

    role_id = Column(Integer, ForeignKey("role.role_id", ondelete="CASCADE"), primary_key=True)
    policy_id = Column(Integer, ForeignKey("policy.policy_id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    role = relationship("Role", back_populates="role_policies")
    policy = relationship("Policy", back_populates="role_policies")


# ==============================================================================
# AUDIT TABLES
# ==============================================================================

class AuthorizationAudit(Base):
    """AuthorizationAudit table - logs all authorization decisions."""
    __tablename__ = "authorization_audit"

    audit_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, nullable=False)
    user_id = Column(Integer)
    resource = Column(String(100))
    action = Column(String(20))
    decision = Column(String(10))  # ALLOW or DENY
    reason = Column(String(255))
    payload_hash = Column(String(64))  # SHA256 hash of payload
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_auth_audit_org_time', 'organization_id', 'created_at'),
    )


# ==============================================================================
# EMISSION FACTOR TABLE
# ==============================================================================

class EmissionFactor(Base):
    """Emission Factor table - holds factors to convert activity data to CO₂e."""
    __tablename__ = "emission_factor"

    factor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    standard_source = Column(String(100))
    unit = Column(String(100))
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
# EMISSION ACTIVITY & CALCULATION TABLES
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
    source_reference = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
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
    factor_id = Column(Integer, ForeignKey("emission_factor.factor_id"), nullable=True)
    co2e_value = Column(DECIMAL(18, 4), nullable=False)
    calculation_method = Column(String(100))
    factor_used = Column(String(255))
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    activity = relationship("EmissionActivity", back_populates="calculations")
    emission_factor = relationship("EmissionFactor")


# ==============================================================================
# SCOPE 1 SUBTABLES
# ==============================================================================

class StationaryFuel(Base):
    """Stationary Fuel - Scope 1 subtable for stationary combustion."""
    __tablename__ = "stationary_fuel"

    fuel_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100))  
    fuel_type_id = Column(Integer, ForeignKey("fuel_type.fuel_type_id"), nullable=False)
    fuel=Column(String(100))
    quantity = Column(DECIMAL(18, 4), nullable=False)
    unit = Column(String(50), nullable=False)
    factor_id = Column(Integer, ForeignKey("emission_factor.factor_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    activity = relationship("EmissionActivity", back_populates="stationary_fuels")
    emission_factor = relationship("EmissionFactor", back_populates="stationary_fuels")
    fuel_type = relationship("FuelType")


class CompanyVehicle(Base):
    """Company Vehicle - Scope 1 subtable for mobile combustion."""
    __tablename__ = "company_vehicle"

    vehicle_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    vehicle_type = Column(String(100), nullable=False)
    vehicle_size = Column(String(100))
    fuel = Column(String(100))
    category = Column(String(100))
    distance_travelled = Column(DECIMAL(18, 4))
    fuel_consumed = Column(DECIMAL(18, 4))
    factor_id = Column(Integer, ForeignKey("emission_factor.factor_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    activity = relationship("EmissionActivity", back_populates="company_vehicles")
    emission_factor = relationship("EmissionFactor", back_populates="company_vehicles")


class RefrigerantLeak(Base):
    """Refrigerant Leak - Scope 1 subtable for fugitive emissions."""
    __tablename__ = "refrigerant_leak"

    refrigerant_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100))
    refrigerant = Column(String(100), nullable=False)
    leak_quantity_kg = Column(DECIMAL(18, 4), nullable=False)
    gwp_factor = Column(DECIMAL(18, 4))
    factor_id = Column(Integer, ForeignKey("emission_factor.factor_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    activity = relationship("EmissionActivity", back_populates="refrigerant_leaks")
    emission_factor = relationship("EmissionFactor", back_populates="refrigerant_leaks")


class ProcessEmission(Base):
    """Process Emission - Scope 1 subtable for industrial process emissions."""
    __tablename__ = "process_emission"

    process_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("emission_activity.activity_id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100))
    material = Column(String(100), nullable=False)
    quantity_processed = Column(DECIMAL(18, 4), nullable=False)
    unit = Column(String(50))
    factor_id = Column(Integer, ForeignKey("emission_factor.factor_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    activity = relationship("EmissionActivity", back_populates="process_emissions")
    emission_factor = relationship("EmissionFactor", back_populates="process_emissions")


__all__ = [
    # Master Tables
    "Organization",
    "User",
    "Facility",
    "Supplier",
    "FuelType",
    "Scope",
    "Unit",
    "Sector",
    # RBAC Tables
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    # Field Security Tables
    "ResourceField",
    "FieldPermission",
    # ABAC Tables
    "Policy",
    "RolePolicy",
    # Audit Tables
    "AuthorizationAudit",
    # Emission Tables
    "EmissionFactor",
    "EmissionActivity",
    "EmissionCalculation",
    "StationaryFuel",
    "CompanyVehicle",
    "RefrigerantLeak",
    "ProcessEmission",
]
