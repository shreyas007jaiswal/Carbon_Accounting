"""Company Vehicle Schemas (Scope 1)"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CompanyVehicleBase(BaseModel):
    vehicle_type: str = Field(..., max_length=100)
    distance_travelled: Optional[Decimal] = None
    fuel_consumed: Optional[Decimal] = None
    factor_id: Optional[int] = None


class CompanyVehicleCreate(CompanyVehicleBase):
    activity_id: int


class CompanyVehicleResponse(CompanyVehicleBase):
    vehicle_id: int
    activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True
