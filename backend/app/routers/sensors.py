from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..database import get_db
from typing import List
from uuid import UUID
from .auth import get_current_user

router = APIRouter(prefix="/sensors", tags=["sensors"])

@router.post("/", response_model=schemas.SensorRead, status_code=status.HTTP_201_CREATED)
def create_sensor(sensor: schemas.SensorCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_sensor = models.Sensor(**sensor.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

@router.get("/", response_model=List[schemas.SensorRead])
def list_sensors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Sensor).offset(skip).limit(limit).all()

@router.get("/{sensor_id}", response_model=schemas.SensorRead)
def get_sensor(sensor_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor

@router.put("/{sensor_id}", response_model=schemas.SensorRead)
def update_sensor(sensor_id: UUID, sensor_update: schemas.SensorCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    for key, value in sensor_update.dict().items():
        setattr(sensor, key, value)
    db.commit()
    db.refresh(sensor)
    return sensor

@router.delete("/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sensor(sensor_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    db.delete(sensor)
    db.commit()
    return None

@router.get("/by_device/{device_id}", response_model=List[schemas.SensorRead])
def list_sensors_by_device(device_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow if user owns or has access to the device
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to view sensors for this device")
    return db.query(models.Sensor).filter(models.Sensor.device_id == device_id).all()
