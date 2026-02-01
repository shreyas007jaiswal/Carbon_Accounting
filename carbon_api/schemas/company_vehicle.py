"""Company Vehicle Pydantic Schemas (Scope 1)"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class CompanyVehicleBase(BaseModel):
    """Base schema for company vehicle."""
    activity_id: int
    vehicle_type: str  # Car, Van, HGV
    vehicle_size: Optional[str] = None  # Small, Medium, Large
    fuel: Optional[str] = None  # Petrol, Diesel, Hybrid, Electric
    category: Optional[str] = None  # Optional categorisation
    distance_travelled: Optional[Decimal] = None  # km
    fuel_consumed: Optional[Decimal] = None  # litres
    factor_id: Optional[int] = None


class CompanyVehicleCreate(CompanyVehicleBase):
    """Schema for creating a company vehicle record."""
    pass


class CompanyVehicleResponse(CompanyVehicleBase):
    """Schema for company vehicle response."""
    vehicle_id: int
    created_at: datetime

    class Config:
        from_attributes = True
