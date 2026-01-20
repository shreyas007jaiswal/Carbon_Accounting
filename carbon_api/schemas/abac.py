"""ABAC Pydantic Schemas - Policy, RolePolicy"""

from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel


# ==============================================================================
# POLICY SCHEMAS
# ==============================================================================

class PolicyBase(BaseModel):
    """Base schema for Policy."""
    name: Optional[str] = None
    resource: str  # EMISSION, REPORT, etc.
    action: str  # CREATE, READ, UPDATE, DELETE
    conditions: Dict[str, Any]  # JSON conditions
    description: Optional[str] = None


class PolicyCreate(PolicyBase):
    """Schema for creating a policy."""
    organization_id: int


class PolicyUpdate(BaseModel):
    """Schema for updating a policy."""
    name: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class PolicyResponse(PolicyBase):
    """Schema for policy response."""
    policy_id: int
    organization_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# ROLE POLICY SCHEMAS
# ==============================================================================

class RolePolicyBase(BaseModel):
    """Base schema for RolePolicy."""
    role_id: int
    policy_id: int


class RolePolicyCreate(RolePolicyBase):
    """Schema for creating a role-policy mapping."""
    pass


class RolePolicyResponse(RolePolicyBase):
    """Schema for role-policy response."""
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# POLICY CONDITION SCHEMAS (for validation)
# ==============================================================================

class PolicyCondition(BaseModel):
    """Schema for a single policy condition."""
    eq: Optional[Any] = None  # equals
    lt: Optional[float] = None  # less than
    gt: Optional[float] = None  # greater than
    neq: Optional[Any] = None  # not equal
    in_: Optional[str] = None  # membership (e.g., "user.facility_ids")

    class Config:
        populate_by_name = True
        # Allow 'in' as alias for 'in_'
        fields = {'in_': {'alias': 'in'}}


# ==============================================================================
# COMPOSITE SCHEMAS
# ==============================================================================

class PolicyWithRoles(PolicyResponse):
    """Policy with linked roles."""
    roles: List[int] = []  # List of role_ids


class RoleWithPolicies(BaseModel):
    """Role with its policies."""
    role_id: int
    name: str
    policies: List[PolicyResponse] = []

    class Config:
        from_attributes = True
