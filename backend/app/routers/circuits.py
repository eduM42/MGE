from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..database import get_db
from typing import List
from uuid import UUID
from .auth import get_current_user

router = APIRouter(prefix="/circuits", tags=["circuits"])

@router.post("/", response_model=schemas.CircuitRead, status_code=status.HTTP_201_CREATED)
def create_circuit(circuit: schemas.CircuitCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_circuit = models.Circuit(**circuit.dict())
    db.add(db_circuit)
    db.commit()
    db.refresh(db_circuit)
    return db_circuit

@router.get("/", response_model=List[schemas.CircuitRead])
def list_circuits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Circuit).offset(skip).limit(limit).all()

@router.get("/{circuit_id}", response_model=schemas.CircuitRead)
def get_circuit(circuit_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    circuit = db.query(models.Circuit).filter(models.Circuit.id == circuit_id).first()
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    return circuit

@router.put("/{circuit_id}", response_model=schemas.CircuitRead)
def update_circuit(circuit_id: UUID, circuit_update: schemas.CircuitCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    circuit = db.query(models.Circuit).filter(models.Circuit.id == circuit_id).first()
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    for key, value in circuit_update.dict().items():
        setattr(circuit, key, value)
    db.commit()
    db.refresh(circuit)
    return circuit

@router.delete("/{circuit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_circuit(circuit_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    circuit = db.query(models.Circuit).filter(models.Circuit.id == circuit_id).first()
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    db.delete(circuit)
    db.commit()
    return None
