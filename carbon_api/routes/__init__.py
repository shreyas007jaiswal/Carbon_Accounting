"""
Routes Package
Exports all API routers for the Carbon Accounting API.
Includes Master Tables, RBAC, ABAC, Field Security, and Audit routes.
"""

# Master Table Routes
from .organization import router as organization_router
from .user import router as user_router
from .facility import router as facility_router
from .supplier import router as supplier_router

# Emission Routes
from .emission_factor import router as emission_factor_router
from .emission_activity import router as emission_activity_router
from .emission_calculation import router as emission_calculation_router

# Scope 1 Subtable Routes
from .stationary_fuel import router as stationary_fuel_router
from .company_vehicle import router as company_vehicle_router
from .refrigerant_leak import router as refrigerant_leak_router
from .process_emission import router as process_emission_router

# RBAC Routes
from .rbac import roles_router, permissions_router, user_roles_router

# Field Security Routes
from .field_security import resource_fields_router, field_permissions_router, roles_fields_router

# ABAC Routes
from .abac import policies_router, role_policies_router

# Audit Routes
from .audit import router as audit_router

# Health Route
from .health import router as health_router


__all__ = [
    # Master Tables
    "organization_router",
    "user_router",
    "facility_router",
    "supplier_router",
    # Emissions
    "emission_factor_router",
    "emission_activity_router",
    "emission_calculation_router",
    # Scope 1 Subtables
    "stationary_fuel_router",
    "company_vehicle_router",
    "refrigerant_leak_router",
    "process_emission_router",
    # RBAC
    "roles_router",
    "permissions_router",
    "user_roles_router",
    # Field Security
    "resource_fields_router",
    "field_permissions_router",
    "roles_fields_router",
    # ABAC
    "policies_router",
    "role_policies_router",
    # Audit
    "audit_router",
    # Health
    "health_router",
]
