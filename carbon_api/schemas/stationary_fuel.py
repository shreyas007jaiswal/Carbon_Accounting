"""Stationary Fuel Schemas (Scope 1)"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class StationaryFuelBase(BaseModel):
    fuel_type: str = Field(..., max_length=100)
    quantity: Decimal
    unit: str = Field(..., max_length=50)
    factor_id: Optional[int] = None


class StationaryFuelCreate(StationaryFuelBase):
    activity_id: int


class StationaryFuelResponse(StationaryFuelBase):
    fuel_id: int
    activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True
