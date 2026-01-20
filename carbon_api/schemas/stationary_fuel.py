"""Stationary Fuel Pydantic Schemas (Scope 1)"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class StationaryFuelBase(BaseModel):
    """Base schema for stationary fuel."""
    activity_id: int
    fuel_category: Optional[str] = None  # Gaseous, Liquid, Solid
    fuel_type: str  # Natural Gas, LPG, Diesel, etc.
    quantity: Decimal
    unit: str  # kWh, litres, tonnes
    factor_id: Optional[int] = None


class StationaryFuelCreate(StationaryFuelBase):
    """Schema for creating a stationary fuel record."""
    pass


class StationaryFuelResponse(StationaryFuelBase):
    """Schema for stationary fuel response."""
    fuel_id: int
    created_at: datetime

    class Config:
        from_attributes = True
