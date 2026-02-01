"""Stationary Fuel API Endpoints (Scope 1)"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import StationaryFuel, EmissionActivity, EmissionFactor, EmissionCalculation, FuelType
from ..schemas.stationary_fuel import StationaryFuelCreate, StationaryFuelResponse
from ..services import find_matching_factor, calculate_co2e


router = APIRouter(prefix="/scope1/stationary-fuels", tags=["Scope 1 - Stationary Fuel"])


@router.post("/", response_model=StationaryFuelResponse, status_code=status.HTTP_201_CREATED)
def create_stationary_fuel(fuel: StationaryFuelCreate, db: Session = Depends(get_db)):
    """Create a new stationary fuel record and auto-calculate CO2e.

    Supports legacy payload fields:
    - fuel_category -> category
    - fuel_type -> fuel
    """
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == fuel.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")

    # Map legacy fields
    category = fuel.category or fuel.fuel_category
    fuel_name = fuel.fuel or fuel.fuel_type

    if not category and not fuel.fuel_type_id:
        raise HTTPException(
            status_code=422,
            detail="Either 'fuel_type_id' or 'category'/'fuel_category' must be provided."
        )
    if not fuel_name:
        raise HTTPException(
            status_code=422,
            detail="Either 'fuel' or legacy 'fuel_type' must be provided."
        )

    # Resolve / create FuelType dependency
    fuel_type_id = fuel.fuel_type_id
    if not fuel_type_id:
        existing_ft = db.query(FuelType).filter(FuelType.name == category).first()
        if not existing_ft:
            existing_ft = FuelType(name=category)
            db.add(existing_ft)
            db.commit()
            db.refresh(existing_ft)
        fuel_type_id = existing_ft.fuel_type_id

    # Try to find matching emission factor
    factor = None
    if fuel.factor_id:
        factor = db.query(EmissionFactor).filter(EmissionFactor.factor_id == fuel.factor_id).first()
    else:
        # Auto-match based on fuel name and unit
        factor = find_matching_factor(db, category=fuel_name, unit=fuel.unit)

    db_fuel = StationaryFuel(
        activity_id=fuel.activity_id,
        category=category,
        fuel_type_id=fuel_type_id,
        fuel=fuel_name,
        quantity=fuel.quantity,
        unit=fuel.unit,
        factor_id=fuel.factor_id,
    )

    if factor:
        db_fuel.factor_id = factor.factor_id

    db.add(db_fuel)
    db.commit()
    db.refresh(db_fuel)

    # Auto-calculate and create/update emission calculation
    if factor and fuel.quantity:
        co2e_value = calculate_co2e(float(fuel.quantity), float(factor.value))

        existing_calc = db.query(EmissionCalculation).filter(
            EmissionCalculation.activity_id == fuel.activity_id
        ).first()

        factor_used_str = f"{factor.category} ({factor.value} {factor.unit})"

        if existing_calc:
            existing_calc.co2e_value = co2e_value
            existing_calc.calculation_method = "Stationary Fuel Auto-calc"
            existing_calc.factor_used = factor_used_str
            existing_calc.factor_id = factor.factor_id
        else:
            calc = EmissionCalculation(
                activity_id=fuel.activity_id,
                factor_id=factor.factor_id,
                co2e_value=co2e_value,
                calculation_method="Stationary Fuel Auto-calc",
                factor_used=factor_used_str
            )
            db.add(calc)

        db.commit()

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
