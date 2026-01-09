"""Process Emission Schemas (Scope 1)"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ProcessEmissionBase(BaseModel):
    material_type: str = Field(..., max_length=100)
    quantity_processed: Decimal
    factor_id: Optional[int] = None


class ProcessEmissionCreate(ProcessEmissionBase):
    activity_id: int


class ProcessEmissionResponse(ProcessEmissionBase):
    process_id: int
    activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True
