"""
Carbon Accounting API - Main Application
FastAPI application with modular routing.
Includes RBAC, ABAC, Field Security, and Audit endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes import (
    # Master Tables
    organization_router,
    user_router,
    facility_router,
    supplier_router,
    # Emissions
    emission_factor_router,
    emission_activity_router,
    emission_calculation_router,
    # Scope 1 Subtables
    stationary_fuel_router,
    company_vehicle_router,
    refrigerant_leak_router,
    process_emission_router,
    # RBAC
    roles_router,
    permissions_router,
    user_roles_router,
    # Field Security
    resource_fields_router,
    field_permissions_router,
    roles_fields_router,
    # ABAC
    policies_router,
    role_policies_router,
    # Audit
    audit_router,
    # Health
    health_router,
)


app = FastAPI(
    title="Carbon Accounting API",
    description="""
    API for tracking Scope 1, 2, and 3 emissions with comprehensive authorization.
    
    ## Features
    - **Master Tables**: Organizations, Users, Facilities, Suppliers
    - **Emission Tracking**: Activities, Calculations, Emission Factors
    - **Scope 1 Subtables**: Stationary Fuel, Company Vehicles, Refrigerant Leaks, Process Emissions
    - **RBAC**: Roles, Permissions, Role-Permission Mapping, User-Role Assignment
    - **Field Security**: Resource Fields, Field-Level Permissions
    - **ABAC**: Policies with JSON Conditions, Role-Policy Mapping
    - **Audit**: Authorization Audit Logging
    """,
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


# ==============================================================================
# MASTER TABLE ROUTES
# ==============================================================================
app.include_router(organization_router)
app.include_router(user_router)
app.include_router(facility_router)
app.include_router(supplier_router)

# ==============================================================================
# EMISSION ROUTES
# ==============================================================================
app.include_router(emission_factor_router)
app.include_router(emission_activity_router)
app.include_router(emission_calculation_router)

# ==============================================================================
# SCOPE 1 SUBTABLE ROUTES
# ==============================================================================
app.include_router(stationary_fuel_router)
app.include_router(company_vehicle_router)
app.include_router(refrigerant_leak_router)
app.include_router(process_emission_router)

# ==============================================================================
# RBAC ROUTES
# ==============================================================================
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(user_roles_router)

# ==============================================================================
# FIELD SECURITY ROUTES
# ==============================================================================
app.include_router(resource_fields_router)
app.include_router(field_permissions_router)
app.include_router(roles_fields_router)

# ==============================================================================
# ABAC ROUTES
# ==============================================================================
app.include_router(policies_router)
app.include_router(role_policies_router)

# ==============================================================================
# AUDIT ROUTES
# ==============================================================================
app.include_router(audit_router)

# ==============================================================================
# HEALTH ROUTE
# ==============================================================================
app.include_router(health_router)
