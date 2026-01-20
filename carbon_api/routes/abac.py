"""ABAC API Endpoints - Policies, Role-Policy Mapping"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Policy, RolePolicy, Role
from ..schemas.abac import (
    PolicyCreate, PolicyUpdate, PolicyResponse,
    RolePolicyCreate, RolePolicyResponse,
)


# ==============================================================================
# POLICIES
# ==============================================================================

policies_router = APIRouter(prefix="/policies", tags=["ABAC - Policies"])


@policies_router.post("/", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy(policy: PolicyCreate, db: Session = Depends(get_db)):
    """Create a new ABAC policy with JSON conditions."""
    # Validate action
    if policy.action not in ['CREATE', 'READ', 'UPDATE', 'DELETE']:
        raise HTTPException(status_code=400, detail="Action must be CREATE, READ, UPDATE, or DELETE")
    
    # Validate conditions structure
    if not isinstance(policy.conditions, dict):
        raise HTTPException(status_code=400, detail="Conditions must be a JSON object")
    
    db_policy = Policy(**policy.model_dump())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy


@policies_router.get("/", response_model=List[PolicyResponse])
def get_policies(
    organization_id: Optional[int] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all policies with optional filters."""
    query = db.query(Policy)
    if organization_id:
        query = query.filter(Policy.organization_id == organization_id)
    if resource:
        query = query.filter(Policy.resource == resource)
    if action:
        query = query.filter(Policy.action == action)
    return query.all()


@policies_router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
    """Get a specific policy by ID."""
    policy = db.query(Policy).filter(Policy.policy_id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@policies_router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(policy_id: int, update: PolicyUpdate, db: Session = Depends(get_db)):
    """Update a policy."""
    policy = db.query(Policy).filter(Policy.policy_id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    if update.name is not None:
        policy.name = update.name
    if update.conditions is not None:
        policy.conditions = update.conditions
    if update.description is not None:
        policy.description = update.description
    
    db.commit()
    db.refresh(policy)
    return policy


@policies_router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
    """Delete a policy."""
    policy = db.query(Policy).filter(Policy.policy_id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(policy)
    db.commit()


# ==============================================================================
# ROLE-POLICY MAPPING
# ==============================================================================

@policies_router.post("/{policy_id}/roles", response_model=RolePolicyResponse, status_code=status.HTTP_201_CREATED)
def attach_policy_to_role(policy_id: int, role_id: int, db: Session = Depends(get_db)):
    """Attach a policy to a role."""
    policy = db.query(Policy).filter(Policy.policy_id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check organizations match
    if role.organization_id != policy.organization_id:
        raise HTTPException(status_code=400, detail="Policy and role must belong to the same organization")
    
    # Check for existing mapping
    existing = db.query(RolePolicy).filter(
        RolePolicy.role_id == role_id,
        RolePolicy.policy_id == policy_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Policy already attached to role")
    
    db_mapping = RolePolicy(role_id=role_id, policy_id=policy_id)
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping


@policies_router.get("/{policy_id}/roles", response_model=List[int])
def get_policy_roles(policy_id: int, db: Session = Depends(get_db)):
    """Get all roles attached to a policy."""
    policy = db.query(Policy).filter(Policy.policy_id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    role_ids = db.query(RolePolicy.role_id).filter(RolePolicy.policy_id == policy_id).all()
    return [r[0] for r in role_ids]


@policies_router.delete("/{policy_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def detach_policy_from_role(policy_id: int, role_id: int, db: Session = Depends(get_db)):
    """Detach a policy from a role."""
    mapping = db.query(RolePolicy).filter(
        RolePolicy.policy_id == policy_id,
        RolePolicy.role_id == role_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Role-policy mapping not found")
    db.delete(mapping)
    db.commit()


# ==============================================================================
# ROLE POLICIES (Convenience endpoints from role perspective)
# ==============================================================================

role_policies_router = APIRouter(prefix="/roles", tags=["ABAC - Role Policies"])


@role_policies_router.post("/{role_id}/policies", response_model=RolePolicyResponse, status_code=status.HTTP_201_CREATED)
def attach_policy_from_role(role_id: int, policy_id: int, db: Session = Depends(get_db)):
    """Attach a policy to a role (from role perspective)."""
    return attach_policy_to_role(policy_id, role_id, db)


@role_policies_router.get("/{role_id}/policies", response_model=List[PolicyResponse])
def get_role_policies(role_id: int, db: Session = Depends(get_db)):
    """Get all policies attached to a role."""
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    policies = db.query(Policy).join(RolePolicy).filter(RolePolicy.role_id == role_id).all()
    return policies
