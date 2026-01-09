"""
Routes Package
Exports all API routers for the Carbon Accounting API.
"""

from .organization import router as organization_router
from .user import router as user_router
from .facility import router as facility_router
from .supplier import router as supplier_router
from .emission_factor import router as emission_factor_router
from .emission_activity import router as emission_activity_router
from .emission_calculation import router as emission_calculation_router
from .stationary_fuel import router as stationary_fuel_router
from .company_vehicle import router as company_vehicle_router
from .refrigerant_leak import router as refrigerant_leak_router
from .process_emission import router as process_emission_router
from .health import router as health_router


__all__ = [
    "organization_router",
    "user_router",
    "facility_router",
    "supplier_router",
    "emission_factor_router",
    "emission_activity_router",
    "emission_calculation_router",
    "stationary_fuel_router",
    "company_vehicle_router",
    "refrigerant_leak_router",
    "process_emission_router",
    "health_router",
]
