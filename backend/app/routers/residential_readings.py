from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..database import get_db
from typing import List
from uuid import UUID
from .auth import get_current_user

router = APIRouter(prefix="/residential_readings", tags=["residential_readings"])

@router.post("/", response_model=schemas.ResidentialReadingRead, status_code=status.HTTP_201_CREATED)
def create_reading(reading: schemas.ResidentialReadingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow if user owns or has access to the device
    device = db.query(models.Device).filter(models.Device.id == reading.device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=reading.device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to add reading for this device")
    db_reading = models.ResidentialReading(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

@router.get("/", response_model=List[schemas.ResidentialReadingRead])
def list_readings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only return readings for devices the user owns or has access to
    owned_devices = db.query(models.Device.id).filter(models.Device.user_id == current_user.id)
    permitted_devices = db.query(models.UserDeviceAccess.device_id).filter(models.UserDeviceAccess.user_id == current_user.id)
    return db.query(models.ResidentialReading).filter(models.ResidentialReading.device_id.in_(owned_devices.union(permitted_devices))).offset(skip).limit(limit).all()

@router.get("/{reading_id}", response_model=schemas.ResidentialReadingRead)
def get_reading(reading_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    reading = db.query(models.ResidentialReading).filter(models.ResidentialReading.id == reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    device = db.query(models.Device).filter(models.Device.id == reading.device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=reading.device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to view this reading")
    return reading

@router.put("/{reading_id}", response_model=schemas.ResidentialReadingRead)
def update_reading(reading_id: int, reading_update: schemas.ResidentialReadingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    reading = db.query(models.ResidentialReading).filter(models.ResidentialReading.id == reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    device = db.query(models.Device).filter(models.Device.id == reading.device_id).first()
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this reading")
    for key, value in reading_update.dict().items():
        setattr(reading, key, value)
    db.commit()
    db.refresh(reading)
    return reading

@router.delete("/{reading_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reading(reading_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    reading = db.query(models.ResidentialReading).filter(models.ResidentialReading.id == reading_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    device = db.query(models.Device).filter(models.Device.id == reading.device_id).first()
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this reading")
    db.delete(reading)
    db.commit()
    return None

@router.get("/by_device/{device_id}", response_model=List[schemas.ResidentialReadingRead])
def list_readings_by_device(device_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to view readings for this device")
    return db.query(models.ResidentialReading).filter(models.ResidentialReading.device_id == device_id).all()
