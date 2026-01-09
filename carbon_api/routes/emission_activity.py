"""Emission Activity API Endpoints"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import EmissionActivity, Organization, Facility, Supplier
from ..schemas.emission_activity import EmissionActivityCreate, EmissionActivityResponse


router = APIRouter(prefix="/emission-activities", tags=["Emission Activities"])


@router.post("/", response_model=EmissionActivityResponse, status_code=status.HTTP_201_CREATED)
def create_emission_activity(activity: EmissionActivityCreate, db: Session = Depends(get_db)):
    """Create a new emission activity."""
    org = db.query(Organization).filter(Organization.organization_id == activity.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if activity.facility_id:
        facility = db.query(Facility).filter(Facility.facility_id == activity.facility_id).first()
        if not facility:
            raise HTTPException(status_code=404, detail="Facility not found")
    
    if activity.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.supplier_id == activity.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
    
    db_activity = EmissionActivity(**activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


@router.get("/", response_model=List[EmissionActivityResponse])
def get_emission_activities(
    scope: Optional[int] = None,
    organization_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve emission activities with optional filters."""
    query = db.query(EmissionActivity)
    if scope:
        query = query.filter(EmissionActivity.scope == scope)
    if organization_id:
        query = query.filter(EmissionActivity.organization_id == organization_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{activity_id}", response_model=EmissionActivityResponse)
def get_emission_activity(activity_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific emission activity by ID."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_emission_activity(activity_id: int, db: Session = Depends(get_db)):
    """Delete an emission activity (cascades to related Scope 1/2/3 and calculation records)."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    db.delete(activity)
    db.commit()
