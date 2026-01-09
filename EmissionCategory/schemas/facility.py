"""Facility Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FacilityBase(BaseModel):
    name: str = Field(..., max_length=255)
    location_region: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=50)


class FacilityCreate(FacilityBase):
    organization_id: int


class FacilityResponse(FacilityBase):
    facility_id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True
