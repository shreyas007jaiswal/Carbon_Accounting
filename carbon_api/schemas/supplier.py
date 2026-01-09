"""Supplier Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SupplierBase(BaseModel):
    name: str = Field(..., max_length=255)
    category: Optional[str] = Field(None, max_length=255)


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    supplier_id: int
    created_at: datetime

    class Config:
        from_attributes = True
