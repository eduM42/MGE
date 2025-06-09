from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..database import get_db
from typing import List
from uuid import UUID
from .auth import get_current_user

router = APIRouter(prefix="/triggered_alarms", tags=["triggered_alarms"])

@router.post("/", response_model=schemas.TriggeredAlarmRead, status_code=status.HTTP_201_CREATED)
def create_triggered_alarm(triggered: schemas.TriggeredAlarmCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow if user owns or has access to the device
    device = db.query(models.Device).filter(models.Device.id == triggered.device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=triggered.device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to add triggered alarm for this device")
    db_triggered = models.TriggeredAlarm(**triggered.dict())
    db.add(db_triggered)
    db.commit()
    db.refresh(db_triggered)
    return db_triggered

@router.get("/", response_model=List[schemas.TriggeredAlarmRead])
def list_triggered_alarms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only return triggered alarms for devices the user owns or has access to
    owned_devices = db.query(models.Device.id).filter(models.Device.user_id == current_user.id)
    permitted_devices = db.query(models.UserDeviceAccess.device_id).filter(models.UserDeviceAccess.user_id == current_user.id)
    triggered_alarms = db.query(models.TriggeredAlarm).filter(models.TriggeredAlarm.device_id.in_(owned_devices.union(permitted_devices))).offset(skip).limit(limit).all()
    # Attach device_name and alarm_name
    result = []
    for ta in triggered_alarms:
        device_name = ta.device.pretty_name if ta.device else str(ta.device_id)
        alarm_name = ta.alarm.name if ta.alarm else str(ta.alarm_id)
        ta_dict = ta.__dict__.copy()
        ta_dict['device_name'] = device_name
        ta_dict['alarm_name'] = alarm_name
        result.append(schemas.TriggeredAlarmRead(**ta_dict))
    return result

@router.get("/{triggered_id}", response_model=schemas.TriggeredAlarmRead)
def get_triggered_alarm(triggered_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    triggered = db.query(models.TriggeredAlarm).filter(models.TriggeredAlarm.id == triggered_id).first()
    if not triggered:
        raise HTTPException(status_code=404, detail="Triggered alarm not found")
    device = db.query(models.Device).filter(models.Device.id == triggered.device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=triggered.device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to view this triggered alarm")
    return triggered

@router.delete("/{triggered_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_triggered_alarm(triggered_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    triggered = db.query(models.TriggeredAlarm).filter(models.TriggeredAlarm.id == triggered_id).first()
    if not triggered:
        raise HTTPException(status_code=404, detail="Triggered alarm not found")
    device = db.query(models.Device).filter(models.Device.id == triggered.device_id).first()
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this triggered alarm")
    db.delete(triggered)
    db.commit()
    return None

@router.get("/by_device/{device_id}", response_model=List[schemas.TriggeredAlarmRead])
def list_triggered_alarms_by_device(device_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to view triggered alarms for this device")
    return db.query(models.TriggeredAlarm).filter(models.TriggeredAlarm.device_id == device_id).all()

@router.get("/by_alarm/{alarm_id}", response_model=List[schemas.TriggeredAlarmRead])
def list_triggered_alarms_by_alarm(alarm_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.TriggeredAlarm).filter(models.TriggeredAlarm.alarm_id == alarm_id).all()
