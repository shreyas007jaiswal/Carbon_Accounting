"""Stationary Fuel Pydantic Schemas (Scope 1)"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class StationaryFuelBase(BaseModel):
    """Base schema for stationary fuel."""
    activity_id: int
    # Backwards-compatible inputs:
    fuel_category: Optional[str] = Field(None, description="Legacy: Gaseous, Liquid, Solid")
    fuel_type: Optional[str] = Field(None, description="Legacy: Natural Gas, LPG, Diesel, etc.")

    # Current fields:
    category: Optional[str] = Field(None, description="Gaseous, Liquid, Solid")
    fuel_type_id: Optional[int] = Field(None, description="FK to fuel_type master table")
    fuel: Optional[str] = Field(None, description="Natural Gas, LPG, Diesel, etc.")

    quantity: Decimal
    unit: str  # kWh, litres, tonnes
    factor_id: Optional[int] = None

    class Config:
        populate_by_name = True


class StationaryFuelCreate(StationaryFuelBase):
    """Schema for creating a stationary fuel record."""
    pass


class StationaryFuelResponse(StationaryFuelBase):
    """Schema for stationary fuel response."""
    fuel_id: int
    created_at: datetime

    class Config:
        from_attributes = True
