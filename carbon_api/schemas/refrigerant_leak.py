"""Refrigerant Leak Pydantic Schemas (Scope 1)"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class RefrigerantLeakBase(BaseModel):
    """Base schema for refrigerant leak."""
    activity_id: int
    category: Optional[str] = None  # HFC, PFC, etc.
    refrigerant: str  # R-410A, R-134a, R-404A
    leak_quantity_kg: Decimal
    gwp_factor: Optional[Decimal] = None  # Global Warming Potential
    factor_id: Optional[int] = None


class RefrigerantLeakCreate(RefrigerantLeakBase):
    """Schema for creating a refrigerant leak record."""
    pass


class RefrigerantLeakResponse(RefrigerantLeakBase):
    """Schema for refrigerant leak response."""
    refrigerant_id: int
    created_at: datetime

    class Config:
        from_attributes = True
