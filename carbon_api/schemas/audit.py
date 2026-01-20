"""Authorization Audit Pydantic Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ==============================================================================
# AUTHORIZATION AUDIT SCHEMAS
# ==============================================================================

class AuthorizationAuditBase(BaseModel):
    """Base schema for AuthorizationAudit."""
    organization_id: int
    user_id: Optional[int] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    decision: str  # ALLOW or DENY
    reason: Optional[str] = None
    payload_hash: Optional[str] = None


class AuthorizationAuditCreate(AuthorizationAuditBase):
    """Schema for creating an audit log entry."""
    pass


class AuthorizationAuditResponse(AuthorizationAuditBase):
    """Schema for audit log response."""
    audit_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==============================================================================
# QUERY SCHEMAS
# ==============================================================================

class AuditQuery(BaseModel):
    """Schema for querying audit logs."""
    user_id: Optional[int] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    decision: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0
