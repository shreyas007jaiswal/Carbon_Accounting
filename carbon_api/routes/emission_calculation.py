"""Emission Calculation API Endpoints"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import EmissionCalculation, EmissionActivity, EmissionFactor
from ..schemas.emission_calculation import EmissionCalculationCreate, EmissionCalculationResponse
from ..services import recalculate_all_emissions, get_emissions_summary, find_matching_factor, calculate_co2e


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


@router.get("/summary")
def get_calculation_summary(organization_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Get a summary of total emissions by scope.
    Optionally filter by organization.
    """
    return get_emissions_summary(db, organization_id)


@router.get("/with-details")
def get_calculations_with_details(
    organization_id: Optional[int] = None,
    scope: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get emission calculations with activity details.
    """
    query = db.query(
        EmissionCalculation.calculation_id,
        EmissionCalculation.co2e_value,
        EmissionCalculation.calculation_method,
        EmissionCalculation.factor_used,
        EmissionCalculation.calculated_at,
        EmissionActivity.activity_id,
        EmissionActivity.scope,
        EmissionActivity.category,
        EmissionActivity.quantity,
        EmissionActivity.unit,
        EmissionActivity.activity_date,
        EmissionActivity.organization_id
    ).join(
        EmissionActivity,
        EmissionCalculation.activity_id == EmissionActivity.activity_id
    )
    
    if organization_id:
        query = query.filter(EmissionActivity.organization_id == organization_id)
    if scope:
        query = query.filter(EmissionActivity.scope == scope)
    
    results = query.offset(skip).limit(limit).all()
    
    return [
        {
            "calculation_id": r[0],
            "co2e_value": float(r[1]) if r[1] else 0,
            "calculation_method": r[2],
            "factor_used": r[3],
            "calculated_at": r[4],
            "activity_id": r[5],
            "scope": r[6],
            "category": r[7],
            "quantity": float(r[8]) if r[8] else 0,
            "unit": r[9],
            "activity_date": r[10],
            "organization_id": r[11]
        }
        for r in results
    ]


@router.post("/recalculate-all")
def recalculate_all(db: Session = Depends(get_db)):
    """
    Recalculate emissions for all activities that don't have calculations.
    Useful after importing new emission factors.
    """
    result = recalculate_all_emissions(db)
    return result


@router.get("/by-scope")
def get_emissions_by_scope(db: Session = Depends(get_db)):
    """
    Get total emissions grouped by scope.
    """
    results = db.query(
        EmissionActivity.scope,
        func.sum(EmissionCalculation.co2e_value).label('total_co2e'),
        func.count(EmissionCalculation.calculation_id).label('count')
    ).join(
        EmissionCalculation,
        EmissionActivity.activity_id == EmissionCalculation.activity_id
    ).group_by(
        EmissionActivity.scope
    ).all()
    
    return [
        {
            "scope": r[0],
            "total_co2e_kg": float(r[1]) if r[1] else 0,
            "total_co2e_tonnes": float(r[1]) / 1000 if r[1] else 0,
            "activity_count": r[2]
        }
        for r in results
    ]


@router.get("/by-category")
def get_emissions_by_category(db: Session = Depends(get_db)):
    """
    Get total emissions grouped by category.
    """
    results = db.query(
        EmissionActivity.category,
        EmissionActivity.scope,
        func.sum(EmissionCalculation.co2e_value).label('total_co2e'),
        func.count(EmissionCalculation.calculation_id).label('count')
    ).join(
        EmissionCalculation,
        EmissionActivity.activity_id == EmissionCalculation.activity_id
    ).group_by(
        EmissionActivity.category,
        EmissionActivity.scope
    ).order_by(
        func.sum(EmissionCalculation.co2e_value).desc()
    ).all()
    
    return [
        {
            "category": r[0],
            "scope": r[1],
            "total_co2e_kg": float(r[2]) if r[2] else 0,
            "total_co2e_tonnes": float(r[2]) / 1000 if r[2] else 0,
            "activity_count": r[3]
        }
        for r in results
    ]
