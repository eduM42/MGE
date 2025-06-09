from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..database import get_db
from typing import List
from uuid import UUID
from .auth import get_current_user

router = APIRouter(prefix="/alarms", tags=["alarms"])

@router.post("/", response_model=schemas.AlarmRead, status_code=status.HTTP_201_CREATED)
def create_alarm(alarm: schemas.AlarmCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    alarm_data = alarm.dict(by_alias=True)
    if 'global' in alarm_data:
        alarm_data['global_'] = alarm_data.pop('global')
    db_alarm = models.Alarm(**alarm_data)
    db.add(db_alarm)
    db.commit()
    db.refresh(db_alarm)
    return db_alarm

@router.get("/", response_model=List[schemas.AlarmRead])
def list_alarms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Alarm).offset(skip).limit(limit).all()

@router.get("/{alarm_id}", response_model=schemas.AlarmRead)
def get_alarm(alarm_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    alarm = db.query(models.Alarm).filter(models.Alarm.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    return alarm

@router.put("/{alarm_id}", response_model=schemas.AlarmRead)
def update_alarm(alarm_id: UUID, alarm_update: schemas.AlarmCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    alarm = db.query(models.Alarm).filter(models.Alarm.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    update_data = alarm_update.dict(by_alias=True)
    if 'global' in update_data:
        update_data['global_'] = update_data.pop('global')
    for key, value in update_data.items():
        setattr(alarm, key, value)
    db.commit()
    db.refresh(alarm)
    return alarm

@router.patch("/{alarm_id}", response_model=schemas.AlarmRead)
def patch_alarm(alarm_id: UUID, patch_data: dict = Body(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    alarm = db.query(models.Alarm).filter(models.Alarm.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    # Map 'global' to 'global_' if present
    if 'global' in patch_data:
        patch_data['global_'] = patch_data.pop('global')
    for key, value in patch_data.items():
        if hasattr(alarm, key):
            setattr(alarm, key, value)
    db.commit()
    db.refresh(alarm)
    return alarm

@router.delete("/{alarm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alarm(alarm_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    alarm = db.query(models.Alarm).filter(models.Alarm.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    db.delete(alarm)
    db.commit()
    return None

@router.get("/by_device/{device_id}", response_model=List[schemas.AlarmRead])
def list_alarms_by_device(device_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow if user owns or has access to the device
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to view alarms for this device")
    return db.query(models.Alarm).filter(models.Alarm.device_id == device_id).all()

@router.get("/by_organization/{org_id}", response_model=List[schemas.AlarmRead])
def list_alarms_by_organization(org_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Alarm).filter(models.Alarm.organization_id == org_id).all()

@router.get("/by_user/{user_id}", response_model=List[schemas.AlarmRead])
def list_alarms_by_user(user_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow if current user is the user in question
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to view alarms for this user")
    return db.query(models.Alarm).filter(models.Alarm.user_id == user_id).all()
