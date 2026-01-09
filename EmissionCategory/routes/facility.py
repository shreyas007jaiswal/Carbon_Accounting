"""Facility API Endpoints"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Facility, Organization
from ..schemas.facility import FacilityCreate, FacilityResponse


router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.post("/", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED)
def create_facility(facility: FacilityCreate, db: Session = Depends(get_db)):
    """Create a new facility."""
    org = db.query(Organization).filter(Organization.organization_id == facility.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    db_facility = Facility(**facility.model_dump())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility


@router.get("/", response_model=List[FacilityResponse])
def get_facilities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all facilities."""
    return db.query(Facility).offset(skip).limit(limit).all()


@router.get("/{facility_id}", response_model=FacilityResponse)
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific facility by ID."""
    facility = db.query(Facility).filter(Facility.facility_id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility
