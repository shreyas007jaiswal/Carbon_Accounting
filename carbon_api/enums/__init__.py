"""
Enums Package
All enumeration types used across the application.
"""

from enum import Enum


class UserRole(str, Enum):
    """User roles within an organization."""
    MANAGER = "Manager"
    ANALYST = "Analyst"
    EMPLOYEE = "Employee"
    SUPPLIER = "Supplier"


class FacilityType(str, Enum):
    """Types of facilities that can emit carbon."""
    OFFICE = "office"
    PLANT = "plant"
    WAREHOUSE = "warehouse"


class ScopeType(int, Enum):
    """GHG Protocol emission scopes."""
    SCOPE_1 = 1
    SCOPE_2 = 2
    SCOPE_3 = 3


class EmissionCategory(str, Enum):
    """Categories of emission activities."""
    FUEL_COMBUSTION = "Fuel Combustion"
    ENERGY = "Energy"
    ELECTRICITY = "Electricity"
    PROCUREMENT = "Procurement"
    TRAVEL = "Travel"
    WASTE = "Waste"
    TRANSPORT = "Transport"
    REFRIGERANT = "Refrigerant"
    PROCESS = "Process"


__all__ = [
    "UserRole",
    "FacilityType",
    "ScopeType",
    "EmissionCategory",
]
