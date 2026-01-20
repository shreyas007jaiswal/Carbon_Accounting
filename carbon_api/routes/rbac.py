"""RBAC API Endpoints - Roles, Permissions, Role-Permission Mapping, User-Role Assignment"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Role, Permission, RolePermission, UserRole, User, Facility
from ..schemas.rbac import (
    RoleCreate, RoleResponse,
    PermissionCreate, PermissionResponse,
    RolePermissionCreate, RolePermissionResponse,
    UserRoleCreate, UserRoleResponse,
)


# ==============================================================================
# ROLES
# ==============================================================================

roles_router = APIRouter(prefix="/roles", tags=["RBAC - Roles"])


@roles_router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """Create a new role for an organization."""
    if role.scope not in ['ORG', 'FACILITY']:
        raise HTTPException(status_code=400, detail="Scope must be 'ORG' or 'FACILITY'")
    
    db_role = Role(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@roles_router.get("/", response_model=List[RoleResponse])
def get_roles(organization_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all roles, optionally filtered by organization."""
    query = db.query(Role)
    if organization_id:
        query = query.filter(Role.organization_id == organization_id)
    return query.all()


@roles_router.get("/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    """Get a specific role by ID."""
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@roles_router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Delete a role."""
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role)
    db.commit()


# ==============================================================================
# PERMISSIONS
# ==============================================================================

permissions_router = APIRouter(prefix="/permissions", tags=["RBAC - Permissions"])


@permissions_router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(permission: PermissionCreate, db: Session = Depends(get_db)):
    """Create a new permission (atomic action on resource)."""
    if permission.action not in ['CREATE', 'READ', 'UPDATE', 'DELETE']:
        raise HTTPException(status_code=400, detail="Action must be CREATE, READ, UPDATE, or DELETE")
    
    # Check for duplicate
    existing = db.query(Permission).filter(
        Permission.resource == permission.resource,
        Permission.action == permission.action
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    db_permission = Permission(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


@permissions_router.get("/", response_model=List[PermissionResponse])
def get_permissions(resource: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all permissions, optionally filtered by resource."""
    query = db.query(Permission)
    if resource:
        query = query.filter(Permission.resource == resource)
    return query.all()


@permissions_router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(permission_id: int, db: Session = Depends(get_db)):
    """Get a specific permission by ID."""
    permission = db.query(Permission).filter(Permission.permission_id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


# ==============================================================================
# ROLE-PERMISSION MAPPING
# ==============================================================================

@roles_router.post("/{role_id}/permissions", response_model=RolePermissionResponse, status_code=status.HTTP_201_CREATED)
def assign_permission_to_role(role_id: int, permission_id: int, db: Session = Depends(get_db)):
    """Assign a permission to a role."""
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    permission = db.query(Permission).filter(Permission.permission_id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Check for existing mapping
    existing = db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission already assigned to role")
    
    db_mapping = RolePermission(role_id=role_id, permission_id=permission_id)
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping


@roles_router.get("/{role_id}/permissions", response_model=List[PermissionResponse])
def get_role_permissions(role_id: int, db: Session = Depends(get_db)):
    """Get all permissions assigned to a role."""
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    permissions = db.query(Permission).join(RolePermission).filter(
        RolePermission.role_id == role_id
    ).all()
    return permissions


@roles_router.delete("/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_permission_from_role(role_id: int, permission_id: int, db: Session = Depends(get_db)):
    """Remove a permission from a role."""
    mapping = db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Role-permission mapping not found")
    db.delete(mapping)
    db.commit()


# ==============================================================================
# USER-ROLE ASSIGNMENT
# ==============================================================================

user_roles_router = APIRouter(prefix="/users", tags=["RBAC - User Roles"])


@user_roles_router.post("/{user_id}/roles", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
def assign_role_to_user(user_id: int, role_id: int, facility_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Assign a role to a user, optionally scoped to a facility."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Validate facility if provided
    if facility_id:
        facility = db.query(Facility).filter(Facility.facility_id == facility_id).first()
        if not facility:
            raise HTTPException(status_code=404, detail="Facility not found")
        if facility.organization_id != user.organization_id:
            raise HTTPException(status_code=400, detail="Facility does not belong to user's organization")
    
    # Check for existing assignment
    existing = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
        UserRole.facility_id == facility_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already assigned to user")
    
    db_assignment = UserRole(user_id=user_id, role_id=role_id, facility_id=facility_id)
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


@user_roles_router.get("/{user_id}/roles", response_model=List[UserRoleResponse])
def get_user_roles(user_id: int, db: Session = Depends(get_db)):
    """Get all roles assigned to a user."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db.query(UserRole).filter(UserRole.user_id == user_id).all()


@user_roles_router.delete("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_role_from_user(user_id: int, role_id: int, facility_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Remove a role assignment from a user."""
    query = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    )
    if facility_id is not None:
        query = query.filter(UserRole.facility_id == facility_id)
    
    assignment = query.first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    db.delete(assignment)
    db.commit()
