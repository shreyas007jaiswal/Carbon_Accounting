"""Refrigerant Leak API Endpoints (Scope 1)"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import RefrigerantLeak, EmissionActivity, EmissionFactor, EmissionCalculation
from ..schemas.refrigerant_leak import RefrigerantLeakCreate, RefrigerantLeakResponse
from ..services import find_matching_factor, calculate_co2e


router = APIRouter(prefix="/scope1/refrigerant-leaks", tags=["Scope 1 - Refrigerant Leaks"])


@router.post("/", response_model=RefrigerantLeakResponse, status_code=status.HTTP_201_CREATED)
def create_refrigerant_leak(leak: RefrigerantLeakCreate, db: Session = Depends(get_db)):
    """Create a new refrigerant leak record and auto-calculate CO2e using GWP."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == leak.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    db_leak = RefrigerantLeak(**leak.model_dump())
    
    # Try to find GWP factor if not provided
    gwp_factor = leak.gwp_factor
    factor = None
    
    if not gwp_factor:
        # Look up GWP from emission factors database
        factor = find_matching_factor(db, category=leak.refrigerant_type, unit="kg")
        if factor:
            gwp_factor = float(factor.value)
            db_leak.gwp_factor = gwp_factor
            db_leak.factor_id = factor.factor_id
    
    db.add(db_leak)
    db.commit()
    db.refresh(db_leak)
    
    # Auto-calculate CO2e if we have GWP and quantity
    if gwp_factor and leak.leak_quantity_kg:
        co2e_value = calculate_co2e(float(leak.leak_quantity_kg), float(gwp_factor))
        
        existing_calc = db.query(EmissionCalculation).filter(
            EmissionCalculation.activity_id == leak.activity_id
        ).first()
        
        factor_info = f"{leak.refrigerant_type} (GWP: {gwp_factor})"
        
        if existing_calc:
            existing_calc.co2e_value = co2e_value
            existing_calc.calculation_method = "Refrigerant GWP Auto-calc"
            existing_calc.factor_used = factor_info
        else:
            calc = EmissionCalculation(
                activity_id=leak.activity_id,
                co2e_value=co2e_value,
                calculation_method="Refrigerant GWP Auto-calc",
                factor_used=factor_info
            )
            db.add(calc)
        
        db.commit()
    
    return db_leak


@router.get("/", response_model=List[RefrigerantLeakResponse])
def get_refrigerant_leaks(activity_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve refrigerant leak records."""
    query = db.query(RefrigerantLeak)
    if activity_id:
        query = query.filter(RefrigerantLeak.activity_id == activity_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{refrigerant_id}", response_model=RefrigerantLeakResponse)
def get_refrigerant_leak(refrigerant_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific refrigerant leak record."""
    leak = db.query(RefrigerantLeak).filter(RefrigerantLeak.refrigerant_id == refrigerant_id).first()
    if not leak:
        raise HTTPException(status_code=404, detail="Refrigerant leak not found")
    return leak
