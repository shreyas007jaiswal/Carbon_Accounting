"""Emission Calculation API Endpoints"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from carbon_api.database import get_db
from carbon_api.models import EmissionCalculation, EmissionActivity
from carbon_api.schemas.emission_calculation import EmissionCalculationCreate, EmissionCalculationResponse


router = APIRouter(prefix="/emission-calculations", tags=["Emission Calculations"])


@router.post("/", response_model=EmissionCalculationResponse, status_code=status.HTTP_201_CREATED)
def create_emission_calculation(calculation: EmissionCalculationCreate, db: Session = Depends(get_db)):
    """Create a new emission calculation."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == calculation.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    db_calc = EmissionCalculation(**calculation.model_dump())
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc


@router.get("/", response_model=List[EmissionCalculationResponse])
def get_emission_calculations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all emission calculations."""
    return db.query(EmissionCalculation).offset(skip).limit(limit).all()
