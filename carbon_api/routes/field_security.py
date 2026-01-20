"""Field Security API Endpoints - ResourceField, FieldPermission"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ResourceField, FieldPermission, Role
from ..schemas.field_security import (
    ResourceFieldCreate, ResourceFieldResponse,
    FieldPermissionCreate, FieldPermissionUpdate, FieldPermissionResponse,
    FieldPermissionWithDetails,
)


# ==============================================================================
# RESOURCE FIELDS
# ==============================================================================

resource_fields_router = APIRouter(prefix="/resource-fields", tags=["Field Security - Resource Fields"])


@resource_fields_router.post("/", response_model=ResourceFieldResponse, status_code=status.HTTP_201_CREATED)
def create_resource_field(field: ResourceFieldCreate, db: Session = Depends(get_db)):
    """Create a new resource field entry."""
    # Check for duplicate
    existing = db.query(ResourceField).filter(
        ResourceField.resource == field.resource,
        ResourceField.field_name == field.field_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Resource field already exists")
    
    db_field = ResourceField(**field.model_dump())
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field


@resource_fields_router.get("/", response_model=List[ResourceFieldResponse])
def get_resource_fields(resource: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all resource fields, optionally filtered by resource."""
    query = db.query(ResourceField)
    if resource:
        query = query.filter(ResourceField.resource == resource)
    return query.all()


@resource_fields_router.get("/{field_id}", response_model=ResourceFieldResponse)
def get_resource_field(field_id: int, db: Session = Depends(get_db)):
    """Get a specific resource field by ID."""
    field = db.query(ResourceField).filter(ResourceField.field_id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Resource field not found")
    return field


@resource_fields_router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource_field(field_id: int, db: Session = Depends(get_db)):
    """Delete a resource field."""
    field = db.query(ResourceField).filter(ResourceField.field_id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Resource field not found")
    db.delete(field)
    db.commit()


# ==============================================================================
# FIELD PERMISSIONS
# ==============================================================================

field_permissions_router = APIRouter(prefix="/field-permissions", tags=["Field Security - Field Permissions"])


@field_permissions_router.post("/", response_model=FieldPermissionResponse, status_code=status.HTTP_201_CREATED)
def create_field_permission(permission: FieldPermissionCreate, db: Session = Depends(get_db)):
    """Create a new field permission."""
    # Validate role exists
    role = db.query(Role).filter(Role.role_id == permission.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Validate field exists
    field = db.query(ResourceField).filter(ResourceField.field_id == permission.field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Resource field not found")
    
    # Check for existing
    existing = db.query(FieldPermission).filter(
        FieldPermission.role_id == permission.role_id,
        FieldPermission.field_id == permission.field_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Field permission already exists")
    
    db_permission = FieldPermission(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


@field_permissions_router.get("/", response_model=List[FieldPermissionWithDetails])
def get_field_permissions(role_id: Optional[int] = None, resource: Optional[str] = None, db: Session = Depends(get_db)):
    """Get field permissions, optionally filtered by role or resource."""
    query = db.query(
        FieldPermission.role_id,
        FieldPermission.field_id,
        ResourceField.resource,
        ResourceField.field_name,
        FieldPermission.can_read,
        FieldPermission.can_update
    ).join(ResourceField)
    
    if role_id:
        query = query.filter(FieldPermission.role_id == role_id)
    if resource:
        query = query.filter(ResourceField.resource == resource)
    
    results = query.all()
    return [
        FieldPermissionWithDetails(
            role_id=r[0],
            field_id=r[1],
            resource=r[2],
            field_name=r[3],
            can_read=r[4],
            can_update=r[5]
        )
        for r in results
    ]


@field_permissions_router.put("/{role_id}/{field_id}", response_model=FieldPermissionResponse)
def update_field_permission(role_id: int, field_id: int, update: FieldPermissionUpdate, db: Session = Depends(get_db)):
    """Update a field permission."""
    permission = db.query(FieldPermission).filter(
        FieldPermission.role_id == role_id,
        FieldPermission.field_id == field_id
    ).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Field permission not found")
    
    if update.can_read is not None:
        permission.can_read = update.can_read
    if update.can_update is not None:
        permission.can_update = update.can_update
    
    db.commit()
    db.refresh(permission)
    return permission


@field_permissions_router.delete("/{role_id}/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field_permission(role_id: int, field_id: int, db: Session = Depends(get_db)):
    """Delete a field permission."""
    permission = db.query(FieldPermission).filter(
        FieldPermission.role_id == role_id,
        FieldPermission.field_id == field_id
    ).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Field permission not found")
    db.delete(permission)
    db.commit()


# ==============================================================================
# ROLE FIELD PERMISSIONS (Convenience endpoints)
# ==============================================================================

roles_fields_router = APIRouter(prefix="/roles", tags=["Field Security - Role Fields"])


@roles_fields_router.get("/{role_id}/fields", response_model=List[FieldPermissionWithDetails])
def get_role_field_permissions(role_id: int, resource: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all field permissions for a role."""
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    query = db.query(
        FieldPermission.role_id,
        FieldPermission.field_id,
        ResourceField.resource,
        ResourceField.field_name,
        FieldPermission.can_read,
        FieldPermission.can_update
    ).join(ResourceField).filter(FieldPermission.role_id == role_id)
    
    if resource:
        query = query.filter(ResourceField.resource == resource)
    
    results = query.all()
    return [
        FieldPermissionWithDetails(
            role_id=r[0],
            field_id=r[1],
            resource=r[2],
            field_name=r[3],
            can_read=r[4],
            can_update=r[5]
        )
        for r in results
    ]
