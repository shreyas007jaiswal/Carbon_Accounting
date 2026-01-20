"""
Enums Package
Contains all enumeration types for the Carbon Accounting API.
Includes RBAC and ABAC enums.
"""

from enum import Enum


class UserRole(str, Enum):
    """Legacy user role enum - kept for backward compatibility."""
    MANAGER = "Manager"
    ANALYST = "Analyst"
    EMPLOYEE = "Employee"
    SUPPLIER = "Supplier"


class RoleScope(str, Enum):
    """Role scope - determines if role is org-wide or facility-specific."""
    ORG = "ORG"
    FACILITY = "FACILITY"


class Action(str, Enum):
    """CRUD actions for permissions."""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class OrganizationStatus(str, Enum):
    """Organization status."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class AuditDecision(str, Enum):
    """Authorization audit decision."""
    ALLOW = "ALLOW"
    DENY = "DENY"


class FacilityType(str, Enum):
    """Facility type."""
    OFFICE = "office"
    PLANT = "plant"
    WAREHOUSE = "warehouse"
    DATA_CENTER = "data_center"
    RETAIL = "retail"


class ScopeType(int, Enum):
    """Emission scope types."""
    SCOPE_1 = 1
    SCOPE_2 = 2
    SCOPE_3 = 3


__all__ = [
    "UserRole",
    "RoleScope",
    "Action",
    "UserStatus",
    "OrganizationStatus",
    "AuditDecision",
    "FacilityType",
    "ScopeType",
]
