"""Emission Activity Schemas"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class EmissionActivityBase(BaseModel):
    scope: int = Field(..., ge=1, le=3)
    category: str = Field(..., max_length=100)
    activity_date: date
    quantity: Optional[Decimal] = None
    unit: Optional[str] = Field(None, max_length=50)
    source_reference: Optional[str] = Field(None, max_length=255)


class EmissionActivityCreate(EmissionActivityBase):
    organization_id: int
    facility_id: Optional[int] = None
    supplier_id: Optional[int] = None


class EmissionActivityResponse(EmissionActivityBase):
    activity_id: int
    organization_id: int
    facility_id: Optional[int]
    supplier_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
