"""Company Vehicle API Endpoints (Scope 1)"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CompanyVehicle, EmissionActivity, EmissionFactor
from ..schemas.company_vehicle import CompanyVehicleCreate, CompanyVehicleResponse


router = APIRouter(prefix="/scope1/company-vehicles", tags=["Scope 1 - Company Vehicles"])


@router.post("/", response_model=CompanyVehicleResponse, status_code=status.HTTP_201_CREATED)
def create_company_vehicle(vehicle: CompanyVehicleCreate, db: Session = Depends(get_db)):
    """Create a new company vehicle record."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == vehicle.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    if vehicle.factor_id:
        factor = db.query(EmissionFactor).filter(EmissionFactor.factor_id == vehicle.factor_id).first()
        if not factor:
            raise HTTPException(status_code=404, detail="Emission factor not found")
    
    db_vehicle = CompanyVehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@router.get("/", response_model=List[CompanyVehicleResponse])
def get_company_vehicles(activity_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve company vehicle records."""
    query = db.query(CompanyVehicle)
    if activity_id:
        query = query.filter(CompanyVehicle.activity_id == activity_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{vehicle_id}", response_model=CompanyVehicleResponse)
def get_company_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific company vehicle record."""
    vehicle = db.query(CompanyVehicle).filter(CompanyVehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Company vehicle not found")
    return vehicle
