"""Process Emission API Endpoints (Scope 1)"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from carbon_api.database import get_db
from carbon_api.models import ProcessEmission, EmissionActivity, EmissionFactor
from carbon_api.schemas.process_emission import ProcessEmissionCreate, ProcessEmissionResponse


router = APIRouter(prefix="/scope1/process-emissions", tags=["Scope 1 - Process Emissions"])


@router.post("/", response_model=ProcessEmissionResponse, status_code=status.HTTP_201_CREATED)
def create_process_emission(process: ProcessEmissionCreate, db: Session = Depends(get_db)):
    """Create a new process emission record."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == process.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    if process.factor_id:
        factor = db.query(EmissionFactor).filter(EmissionFactor.factor_id == process.factor_id).first()
        if not factor:
            raise HTTPException(status_code=404, detail="Emission factor not found")
    
    db_process = ProcessEmission(**process.model_dump())
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    return db_process


@router.get("/", response_model=List[ProcessEmissionResponse])
def get_process_emissions(activity_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve process emission records."""
    query = db.query(ProcessEmission)
    if activity_id:
        query = query.filter(ProcessEmission.activity_id == activity_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{process_id}", response_model=ProcessEmissionResponse)
def get_process_emission(process_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific process emission record."""
    process = db.query(ProcessEmission).filter(ProcessEmission.process_id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Process emission not found")
    return process
