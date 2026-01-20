"""Authorization Audit API Endpoints"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuthorizationAudit
from ..schemas.audit import AuthorizationAuditCreate, AuthorizationAuditResponse


router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/", response_model=List[AuthorizationAuditResponse])
def get_audit_logs(
    organization_id: int,
    user_id: Optional[int] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    decision: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get authorization audit logs with filters."""
    query = db.query(AuthorizationAudit).filter(
        AuthorizationAudit.organization_id == organization_id
    )
    
    if user_id:
        query = query.filter(AuthorizationAudit.user_id == user_id)
    if resource:
        query = query.filter(AuthorizationAudit.resource == resource)
    if action:
        query = query.filter(AuthorizationAudit.action == action)
    if decision:
        query = query.filter(AuthorizationAudit.decision == decision)
    if from_date:
        query = query.filter(AuthorizationAudit.created_at >= from_date)
    if to_date:
        query = query.filter(AuthorizationAudit.created_at <= to_date)
    
    return query.order_by(AuthorizationAudit.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/summary")
def get_audit_summary(organization_id: int, db: Session = Depends(get_db)):
    """Get audit summary statistics."""
    from sqlalchemy import func
    
    total = db.query(func.count(AuthorizationAudit.audit_id)).filter(
        AuthorizationAudit.organization_id == organization_id
    ).scalar()
    
    allowed = db.query(func.count(AuthorizationAudit.audit_id)).filter(
        AuthorizationAudit.organization_id == organization_id,
        AuthorizationAudit.decision == 'ALLOW'
    ).scalar()
    
    denied = db.query(func.count(AuthorizationAudit.audit_id)).filter(
        AuthorizationAudit.organization_id == organization_id,
        AuthorizationAudit.decision == 'DENY'
    ).scalar()
    
    # Get by resource
    by_resource = db.query(
        AuthorizationAudit.resource,
        func.count(AuthorizationAudit.audit_id).label('count')
    ).filter(
        AuthorizationAudit.organization_id == organization_id
    ).group_by(AuthorizationAudit.resource).all()
    
    # Get denial reasons
    denial_reasons = db.query(
        AuthorizationAudit.reason,
        func.count(AuthorizationAudit.audit_id).label('count')
    ).filter(
        AuthorizationAudit.organization_id == organization_id,
        AuthorizationAudit.decision == 'DENY'
    ).group_by(AuthorizationAudit.reason).all()
    
    return {
        "total": total,
        "allowed": allowed,
        "denied": denied,
        "by_resource": [{"resource": r[0], "count": r[1]} for r in by_resource],
        "denial_reasons": [{"reason": r[0], "count": r[1]} for r in denial_reasons]
    }


@router.get("/{audit_id}", response_model=AuthorizationAuditResponse)
def get_audit_log(audit_id: int, db: Session = Depends(get_db)):
    """Get a specific audit log entry."""
    audit = db.query(AuthorizationAudit).filter(AuthorizationAudit.audit_id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return audit
