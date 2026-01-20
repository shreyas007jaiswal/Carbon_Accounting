"""
Schemas Package
Pydantic schemas for request/response validation.
Includes Master Tables, RBAC, ABAC, Field Security, and Audit schemas.
"""

# Master Tables
from .organization import OrganizationBase, OrganizationCreate, OrganizationResponse
from .user import UserBase, UserCreate, UserResponse
from .facility import FacilityBase, FacilityCreate, FacilityResponse
from .supplier import SupplierBase, SupplierCreate, SupplierResponse

# Emission Tables
from .emission_factor import EmissionFactorBase, EmissionFactorCreate, EmissionFactorResponse
from .emission_activity import EmissionActivityBase, EmissionActivityCreate, EmissionActivityResponse
from .emission_calculation import EmissionCalculationBase, EmissionCalculationCreate, EmissionCalculationResponse

# Scope 1 Subtables
from .stationary_fuel import StationaryFuelBase, StationaryFuelCreate, StationaryFuelResponse
from .company_vehicle import CompanyVehicleBase, CompanyVehicleCreate, CompanyVehicleResponse
from .refrigerant_leak import RefrigerantLeakBase, RefrigerantLeakCreate, RefrigerantLeakResponse
from .process_emission import ProcessEmissionBase, ProcessEmissionCreate, ProcessEmissionResponse

# RBAC Schemas
from .rbac import (
    RoleBase, RoleCreate, RoleResponse, RoleWithPermissions,
    PermissionBase, PermissionCreate, PermissionResponse,
    RolePermissionBase, RolePermissionCreate, RolePermissionResponse,
    UserRoleBase, UserRoleCreate, UserRoleResponse, UserWithRoles,
)

# Field Security Schemas
from .field_security import (
    ResourceFieldBase, ResourceFieldCreate, ResourceFieldResponse,
    FieldPermissionBase, FieldPermissionCreate, FieldPermissionUpdate, FieldPermissionResponse,
    FieldPermissionWithDetails,
)

# ABAC Schemas
from .abac import (
    PolicyBase, PolicyCreate, PolicyUpdate, PolicyResponse, PolicyWithRoles,
    RolePolicyBase, RolePolicyCreate, RolePolicyResponse,
    PolicyCondition, RoleWithPolicies,
)

# Audit Schemas
from .audit import (
    AuthorizationAuditBase, AuthorizationAuditCreate, AuthorizationAuditResponse,
    AuditQuery,
)


__all__ = [
    # Master Tables
    "OrganizationBase", "OrganizationCreate", "OrganizationResponse",
    "UserBase", "UserCreate", "UserResponse",
    "FacilityBase", "FacilityCreate", "FacilityResponse",
    "SupplierBase", "SupplierCreate", "SupplierResponse",
    # Emission Tables
    "EmissionFactorBase", "EmissionFactorCreate", "EmissionFactorResponse",
    "EmissionActivityBase", "EmissionActivityCreate", "EmissionActivityResponse",
    "EmissionCalculationBase", "EmissionCalculationCreate", "EmissionCalculationResponse",
    # Scope 1 Subtables
    "StationaryFuelBase", "StationaryFuelCreate", "StationaryFuelResponse",
    "CompanyVehicleBase", "CompanyVehicleCreate", "CompanyVehicleResponse",
    "RefrigerantLeakBase", "RefrigerantLeakCreate", "RefrigerantLeakResponse",
    "ProcessEmissionBase", "ProcessEmissionCreate", "ProcessEmissionResponse",
    # RBAC
    "RoleBase", "RoleCreate", "RoleResponse", "RoleWithPermissions",
    "PermissionBase", "PermissionCreate", "PermissionResponse",
    "RolePermissionBase", "RolePermissionCreate", "RolePermissionResponse",
    "UserRoleBase", "UserRoleCreate", "UserRoleResponse", "UserWithRoles",
    # Field Security
    "ResourceFieldBase", "ResourceFieldCreate", "ResourceFieldResponse",
    "FieldPermissionBase", "FieldPermissionCreate", "FieldPermissionUpdate", "FieldPermissionResponse",
    "FieldPermissionWithDetails",
    # ABAC
    "PolicyBase", "PolicyCreate", "PolicyUpdate", "PolicyResponse", "PolicyWithRoles",
    "RolePolicyBase", "RolePolicyCreate", "RolePolicyResponse",
    "PolicyCondition", "RoleWithPolicies",
    # Audit
    "AuthorizationAuditBase", "AuthorizationAuditCreate", "AuthorizationAuditResponse",
    "AuditQuery",
]
