"""Refrigerant Leak Schemas (Scope 1)"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class RefrigerantLeakBase(BaseModel):
    refrigerant_type: str = Field(..., max_length=100)
    leak_quantity_kg: Decimal
    gwp_factor: Optional[Decimal] = None


class RefrigerantLeakCreate(RefrigerantLeakBase):
    activity_id: int


class RefrigerantLeakResponse(RefrigerantLeakBase):
    refrigerant_id: int
    activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True
