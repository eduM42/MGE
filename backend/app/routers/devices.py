from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..database import get_db
from .auth import get_current_user
from typing import List
from uuid import UUID

router = APIRouter(prefix="/devices", tags=["devices"])

# Device self-registration (no auth)
@router.post("/register", response_model=schemas.DeviceRead, status_code=status.HTTP_201_CREATED)
def register_device_by_device(device: schemas.DeviceRegister, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == device.username).first()
    org = None
    if device.organization_name:
        org = db.query(models.Organization).filter(models.Organization.name == device.organization_name).first()
    db_device = models.Device(
        pretty_name=device.pretty_name,
        user_id=user.id if user else None,
        organization_id=org.id if org else None,
        pending=True
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@router.post("/", response_model=schemas.DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    device_data = device.dict()
    device_data.pop('user_id', None)  # Remove user_id if present
    db_device = models.Device(**device_data, user_id=current_user.id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

# Update list_devices to only return approved devices
@router.get("/", response_model=List[schemas.DeviceRead])
def list_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    owned = db.query(models.Device).filter(models.Device.user_id == current_user.id, models.Device.pending == False)
    permitted = db.query(models.Device).join(models.UserDeviceAccess).filter(models.UserDeviceAccess.user_id == current_user.id, models.Device.pending == False)
    return list(set(owned.all() + permitted.all()))[skip:skip+limit]

@router.get("/pending", response_model=List[schemas.DeviceRead])
def list_pending_devices(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Device).filter(models.Device.user_id == current_user.id, models.Device.pending == True).all()

@router.get("/{device_id}", response_model=schemas.DeviceRead)
def get_device(device_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    # Only allow if user owns or has access
    has_access = (device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=device_id).first()
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to access this device")
    return device

@router.put("/{device_id}", response_model=schemas.DeviceRead)
def update_device(device_id: UUID, device_update: schemas.DeviceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this device")
    for key, value in device_update.dict().items():
        if key == 'user_id':
            continue  # Never overwrite user_id
        setattr(device, key, value)
    # Always keep device approved when editing (unless it's pending)
    if not device.pending:
        device.pending = False
    db.commit()
    db.refresh(device)
    return device

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this device")
    db.delete(device)
    db.commit()
    return None

@router.get("/by_user/{user_id}", response_model=List[schemas.DeviceRead])
def list_devices_by_user(user_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow if current user is the user in question
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to view devices for this user")
    return db.query(models.Device).filter(models.Device.user_id == user_id).all()

@router.get("/by_organization/{org_id}", response_model=List[schemas.DeviceRead])
def list_devices_by_organization(org_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only return devices in the org that the user owns or has access to
    owned = db.query(models.Device).filter(models.Device.organization_id == org_id, models.Device.user_id == current_user.id)
    permitted = db.query(models.Device).join(models.UserDeviceAccess).filter(models.Device.organization_id == org_id, models.UserDeviceAccess.user_id == current_user.id)
    return list(set(owned.all() + permitted.all()))

# Approve a pending device
@router.post("/{device_id}/approve", response_model=schemas.DeviceRead)
def approve_device(device_id: UUID, data: dict = Body(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    device = db.query(models.Device).filter(models.Device.id == device_id, models.Device.user_id == current_user.id, models.Device.pending == True).first()
    if not device:
        raise HTTPException(status_code=404, detail="Pending device not found")
    circuit_id = data.get('circuit_id')
    organization_id = data.get('organization_id')
    if circuit_id:
        device.circuit_id = circuit_id
    if organization_id:
        device.organization_id = organization_id
    device.pending = False
    db.commit()
    db.refresh(device)
    return device

# Deny (delete) a pending device
@router.post("/{device_id}/deny", status_code=status.HTTP_204_NO_CONTENT)
def deny_device(device_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    device = db.query(models.Device).filter(models.Device.id == device_id, models.Device.user_id == current_user.id, models.Device.pending == True).first()
    if not device:
        raise HTTPException(status_code=404, detail="Pending device not found")
    db.delete(device)
    db.commit()
    return None
