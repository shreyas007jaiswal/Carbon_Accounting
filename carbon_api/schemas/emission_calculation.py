"""Emission Calculation Schemas"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class EmissionCalculationBase(BaseModel):
    co2e_value: Decimal
    calculation_method: Optional[str] = Field(None, max_length=100)
    factor_used: Optional[str] = Field(None, max_length=255)


class EmissionCalculationCreate(EmissionCalculationBase):
    activity_id: int


class EmissionCalculationResponse(EmissionCalculationBase):
    calculation_id: int
    activity_id: int
    calculated_at: datetime

    class Config:
        from_attributes = True
