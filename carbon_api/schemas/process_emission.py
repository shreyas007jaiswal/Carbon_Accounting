"""Process Emission Pydantic Schemas (Scope 1)"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ProcessEmissionBase(BaseModel):
    """Base schema for process emission."""
    activity_id: int
    material_category: Optional[str] = None  #ite clinite, Calcium Carbite
    material_type: str
    quantity_processed: Decimal
    unit: Optional[str] = None  # tonnes, kg
    factor_id: Optional[int] = None


class ProcessEmissionCreate(ProcessEmissionBase):
    """Schema for creating a process emission record."""
    pass


class ProcessEmissionResponse(ProcessEmissionBase):
    """Schema for process emission response."""
    process_id: int
    created_at: datetime

    class Config:
        from_attributes = True
