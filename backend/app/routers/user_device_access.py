from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..database import get_db
from .auth import get_current_user
from typing import List
from uuid import UUID

router = APIRouter(prefix="/user_device_access", tags=["user_device_access"])

@router.post("/", response_model=schemas.UserDeviceAccessRead, status_code=status.HTTP_201_CREATED)
def grant_access(access: schemas.UserDeviceAccessCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow granting access if the current user owns the device
    device = db.query(models.Device).filter(models.Device.id == access.device_id).first()
    if not device or (device.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not allowed to grant access to this device")
    db_access = models.UserDeviceAccess(**access.dict())
    db.add(db_access)
    db.commit()
    db.refresh(db_access)
    return db_access

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def revoke_access(user_id: UUID, device_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow revoking access if the current user owns the device
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device or (device.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not allowed to revoke access to this device")
    access = db.query(models.UserDeviceAccess).filter(
        models.UserDeviceAccess.user_id == user_id,
        models.UserDeviceAccess.device_id == device_id
    ).first()
    if not access:
        raise HTTPException(status_code=404, detail="Access not found")
    db.delete(access)
    db.commit()
    return None

@router.get("/by_user/{user_id}", response_model=List[schemas.UserDeviceAccessRead])
def list_access_by_user(user_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow if current user is the user in question
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to view access for this user")
    return db.query(models.UserDeviceAccess).filter(models.UserDeviceAccess.user_id == user_id).all()

@router.get("/by_device/{device_id}", response_model=List[schemas.UserDeviceAccessRead])
def list_access_by_device(device_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow if current user owns the device
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device or (device.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not allowed to view access for this device")
    return db.query(models.UserDeviceAccess).filter(models.UserDeviceAccess.device_id == device_id).all()
