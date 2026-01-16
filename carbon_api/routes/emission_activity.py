"""Emission Activity API Endpoints"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import EmissionActivity, Organization, Facility, Supplier, EmissionCalculation, EmissionFactor
from ..schemas.emission_activity import EmissionActivityCreate, EmissionActivityResponse
from ..services import calculate_activity_emissions, find_matching_factor, calculate_co2e


router = APIRouter(prefix="/emission-activities", tags=["Emission Activities"])


@router.post("/", response_model=EmissionActivityResponse, status_code=status.HTTP_201_CREATED)
def create_emission_activity(activity: EmissionActivityCreate, db: Session = Depends(get_db)):
    """Create a new emission activity and automatically calculate CO2e if possible."""
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
    
    # Auto-calculate emissions if quantity and unit are provided
    if db_activity.quantity and db_activity.unit:
        factor = find_matching_factor(db, category=db_activity.category, unit=db_activity.unit)
        if factor:
            co2e_value = calculate_co2e(float(db_activity.quantity), float(factor.value))
            calc = EmissionCalculation(
                activity_id=db_activity.activity_id,
                co2e_value=co2e_value,
                calculation_method="Auto-calculated",
                factor_used=f"{factor.category} ({factor.value} {factor.unit})"
            )
            db.add(calc)
            db.commit()
    
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


@router.post("/{activity_id}/calculate", status_code=status.HTTP_200_OK)
def calculate_activity_co2e(activity_id: int, db: Session = Depends(get_db)):
    """Manually trigger CO2e calculation for an activity."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    if not activity.quantity or not activity.unit:
        raise HTTPException(status_code=400, detail="Activity must have quantity and unit to calculate")
    
    factor = find_matching_factor(db, category=activity.category, unit=activity.unit)
    if not factor:
        raise HTTPException(status_code=404, detail=f"No emission factor found for category '{activity.category}' with unit '{activity.unit}'")
    
    co2e_value = calculate_co2e(float(activity.quantity), float(factor.value))
    
    # Check for existing calculation
    existing = db.query(EmissionCalculation).filter(EmissionCalculation.activity_id == activity_id).first()
    
    if existing:
        existing.co2e_value = co2e_value
        existing.calculation_method = "Recalculated"
        existing.factor_used = f"{factor.category} ({factor.value} {factor.unit})"
        db.commit()
        return {
            "activity_id": activity_id,
            "co2e_value": co2e_value,
            "factor_used": factor.category,
            "factor_value": float(factor.value),
            "unit": factor.unit,
            "status": "updated"
        }
    else:
        calc = EmissionCalculation(
            activity_id=activity_id,
            co2e_value=co2e_value,
            calculation_method="Manual calculation",
            factor_used=f"{factor.category} ({factor.value} {factor.unit})"
        )
        db.add(calc)
        db.commit()
        return {
            "activity_id": activity_id,
            "co2e_value": co2e_value,
            "factor_used": factor.category,
            "factor_value": float(factor.value),
            "unit": factor.unit,
            "status": "created"
        }
