"""Emission Factor Schemas"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class EmissionFactorBase(BaseModel):
    category: str = Field(..., max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=100)
    value: Decimal
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


class EmissionFactorCreate(EmissionFactorBase):
    pass


class EmissionFactorResponse(EmissionFactorBase):
    factor_id: int
    created_at: datetime

    class Config:
        from_attributes = True
