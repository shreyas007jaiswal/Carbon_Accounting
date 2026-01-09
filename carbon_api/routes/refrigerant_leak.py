"""Refrigerant Leak API Endpoints (Scope 1)"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import RefrigerantLeak, EmissionActivity
from ..schemas.refrigerant_leak import RefrigerantLeakCreate, RefrigerantLeakResponse


router = APIRouter(prefix="/scope1/refrigerant-leaks", tags=["Scope 1 - Refrigerant Leaks"])


@router.post("/", response_model=RefrigerantLeakResponse, status_code=status.HTTP_201_CREATED)
def create_refrigerant_leak(leak: RefrigerantLeakCreate, db: Session = Depends(get_db)):
    """Create a new refrigerant leak record."""
    activity = db.query(EmissionActivity).filter(EmissionActivity.activity_id == leak.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Emission activity not found")
    
    db_leak = RefrigerantLeak(**leak.model_dump())
    db.add(db_leak)
    db.commit()
    db.refresh(db_leak)
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
