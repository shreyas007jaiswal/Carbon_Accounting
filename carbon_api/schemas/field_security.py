"""Field Security Pydantic Schemas - ResourceField, FieldPermission"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ==============================================================================
# RESOURCE FIELD SCHEMAS
# ==============================================================================

class ResourceFieldBase(BaseModel):
    """Base schema for ResourceField."""
    resource: str  # EMISSION, REPORT, etc.
    field_name: str  # quantity, emission_factor, co2e, etc.
    description: Optional[str] = None


class ResourceFieldCreate(ResourceFieldBase):
    """Schema for creating a resource field."""
    pass


class ResourceFieldResponse(ResourceFieldBase):
    """Schema for resource field response."""
    field_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# FIELD PERMISSION SCHEMAS
# ==============================================================================

class FieldPermissionBase(BaseModel):
    """Base schema for FieldPermission."""
    role_id: int
    field_id: int
    can_read: bool = False
    can_update: bool = False


class FieldPermissionCreate(FieldPermissionBase):
    """Schema for creating a field permission."""
    pass


class FieldPermissionUpdate(BaseModel):
    """Schema for updating a field permission."""
    can_read: Optional[bool] = None
    can_update: Optional[bool] = None


class FieldPermissionResponse(FieldPermissionBase):
    """Schema for field permission response."""
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# COMPOSITE SCHEMAS
# ==============================================================================

class FieldPermissionWithDetails(BaseModel):
    """Field permission with resource field details."""
    role_id: int
    field_id: int
    resource: str
    field_name: str
    can_read: bool
    can_update: bool

    class Config:
        from_attributes = True
