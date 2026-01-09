"""Stationary Fuel API Endpoints (Scope 1)"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import StationaryFuel, EmissionActivity, EmissionFactor
from ..schemas.stationary_fuel import StationaryFuelCreate, StationaryFuelResponse


router = APIRouter(prefix="/scope1/stationary-fuels", tags=["Scope 1 - Stationary Fuel"])


@router.post("/", response_model=StationaryFuelResponse, status_code=status.HTTP_201_CREATED)
def create_stationary_fuel(fuel: StationaryFuelCreate, db: Session = Depends(get_db)):
    """Create a new stationary fuel record."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == fuel.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    if fuel.factor_id:
        factor = db.query(EmissionFactor).filter(EmissionFactor.factor_id == fuel.factor_id).first()
        if not factor:
            raise HTTPException(status_code=404, detail="Emission factor not found")
    
    db_fuel = StationaryFuel(**fuel.model_dump())
    db.add(db_fuel)
    db.commit()
    db.refresh(db_fuel)
    return db_fuel


@router.get("/", response_model=List[StationaryFuelResponse])
def get_stationary_fuels(activity_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve stationary fuel records."""
    query = db.query(StationaryFuel)
    if activity_id:
        query = query.filter(StationaryFuel.activity_id == activity_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{fuel_id}", response_model=StationaryFuelResponse)
def get_stationary_fuel(fuel_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific stationary fuel record."""
    fuel = db.query(StationaryFuel).filter(StationaryFuel.fuel_id == fuel_id).first()
    if not fuel:
        raise HTTPException(status_code=404, detail="Stationary fuel not found")
    return fuel
