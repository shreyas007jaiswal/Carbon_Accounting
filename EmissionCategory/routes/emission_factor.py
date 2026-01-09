"""Emission Factor API Endpoints"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from carbon_api.database import get_db
from carbon_api.models import EmissionFactor
from carbon_api.schemas.emission_factor import EmissionFactorCreate, EmissionFactorResponse


router = APIRouter(prefix="/emission-factors", tags=["Emission Factors"])


@router.post("/", response_model=EmissionFactorResponse, status_code=status.HTTP_201_CREATED)
def create_emission_factor(factor: EmissionFactorCreate, db: Session = Depends(get_db)):
    """Create a new emission factor."""
    db_factor = EmissionFactor(**factor.model_dump())
    db.add(db_factor)
    db.commit()
    db.refresh(db_factor)
    return db_factor


@router.get("/", response_model=List[EmissionFactorResponse])
def get_emission_factors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all emission factors."""
    return db.query(EmissionFactor).offset(skip).limit(limit).all()


@router.get("/{factor_id}", response_model=EmissionFactorResponse)
def get_emission_factor(factor_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific emission factor by ID."""
    factor = db.query(EmissionFactor).filter(EmissionFactor.factor_id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Emission factor not found")
    return factor
