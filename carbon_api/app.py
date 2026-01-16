"""
Carbon Accounting API - Main Application
FastAPI application with modular routing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes import (
    organization_router,
    user_router,
    facility_router,
    supplier_router,
    emission_factor_router,
    emission_activity_router,
    emission_calculation_router,
    stationary_fuel_router,
    company_vehicle_router,
    refrigerant_leak_router,
    process_emission_router,
    health_router,
)


app = FastAPI(
    title="Carbon Accounting API",
    description="API for tracking Scope 1, 2, and 3 emissions with master tables and Scope 1 subtables.",
    version="1.0.0",
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("startup")
def startup():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


# Register all routers
app.include_router(organization_router)
app.include_router(user_router)
app.include_router(facility_router)
app.include_router(supplier_router)
app.include_router(emission_factor_router)
app.include_router(emission_activity_router)
app.include_router(emission_calculation_router)
app.include_router(stationary_fuel_router)
app.include_router(company_vehicle_router)
app.include_router(refrigerant_leak_router)
app.include_router(process_emission_router)
app.include_router(health_router)