"""RBAC Pydantic Schemas - Role, Permission, RolePermission, UserRole"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


# ==============================================================================
# ROLE SCHEMAS
# ==============================================================================

class RoleBase(BaseModel):
    """Base schema for Role."""
    name: str
    scope: str  # 'ORG' or 'FACILITY'
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    organization_id: int


class RoleResponse(RoleBase):
    """Schema for role response."""
    role_id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# PERMISSION SCHEMAS
# ==============================================================================

class PermissionBase(BaseModel):
    """Base schema for Permission."""
    resource: str  # EMISSION, REPORT, FACILITY, etc.
    action: str  # CREATE, READ, UPDATE, DELETE
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Schema for creating a permission."""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    permission_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# ROLE PERMISSION SCHEMAS
# ==============================================================================

class RolePermissionBase(BaseModel):
    """Base schema for RolePermission."""
    role_id: int
    permission_id: int


class RolePermissionCreate(RolePermissionBase):
    """Schema for creating a role-permission mapping."""
    pass


class RolePermissionResponse(RolePermissionBase):
    """Schema for role-permission response."""
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# USER ROLE SCHEMAS
# ==============================================================================

class UserRoleBase(BaseModel):
    """Base schema for UserRole."""
    user_id: int
    role_id: int
    facility_id: Optional[int] = None  # Nullable for ORG-wide roles


class UserRoleCreate(UserRoleBase):
    """Schema for creating a user-role assignment."""
    pass


class UserRoleResponse(UserRoleBase):
    """Schema for user-role response."""
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# COMPOSITE SCHEMAS (for API responses)
# ==============================================================================

class RoleWithPermissions(RoleResponse):
    """Role with its permissions."""
    permissions: List[PermissionResponse] = []


class UserWithRoles(BaseModel):
    """User with their role assignments."""
    user_id: int
    email: str
    roles: List[UserRoleResponse] = []

    class Config:
        from_attributes = True
