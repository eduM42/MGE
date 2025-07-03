from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..database import get_db
from typing import List
from uuid import UUID
from .auth import get_current_user

router = APIRouter(prefix="/sensor_packets", tags=["sensor_packets"])

@router.post("/", response_model=schemas.SensorPacketRead, status_code=status.HTTP_201_CREATED)
def create_packet(packet: schemas.SensorPacketCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow if user owns or has access to the device via the sensor
    sensor = db.query(models.Sensor).filter(models.Sensor.id == packet.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    device = db.query(models.Device).filter(models.Device.id == sensor.device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=sensor.device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to add packet for this device")
    db_packet = models.SensorPacket(**packet.dict())
    db.add(db_packet)
    db.commit()
    db.refresh(db_packet)
    return db_packet

@router.get("/", response_model=List[schemas.SensorPacketRead])
def list_packets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only return packets for devices the user owns or has access to
    owned_devices = db.query(models.Device.id).filter(models.Device.user_id == current_user.id)
    permitted_devices = db.query(models.UserDeviceAccess.device_id).filter(models.UserDeviceAccess.user_id == current_user.id)
    sensors = db.query(models.Sensor.id).filter(models.Sensor.device_id.in_(owned_devices.union(permitted_devices)))
    return db.query(models.SensorPacket).filter(models.SensorPacket.sensor_id.in_(sensors)).offset(skip).limit(limit).all()

@router.get("/{packet_id}", response_model=schemas.SensorPacketRead)
def get_packet(packet_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    packet = db.query(models.SensorPacket).filter(models.SensorPacket.id == packet_id).first()
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    sensor = db.query(models.Sensor).filter(models.Sensor.id == packet.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    device = db.query(models.Device).filter(models.Device.id == sensor.device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=sensor.device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to view this packet")
    return packet

@router.delete("/{packet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_packet(packet_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    packet = db.query(models.SensorPacket).filter(models.SensorPacket.id == packet_id).first()
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    sensor = db.query(models.Sensor).filter(models.Sensor.id == packet.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    device = db.query(models.Device).filter(models.Device.id == sensor.device_id).first()
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this packet")
    db.delete(packet)
    db.commit()
    return None

@router.get("/by_device/{device_id}", response_model=List[schemas.SensorPacketRead])
def list_packets_by_device(device_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    has_access = device and ((device.user_id == current_user.id) or db.query(models.UserDeviceAccess).filter_by(user_id=current_user.id, device_id=device_id).first())
    if not has_access:
        raise HTTPException(status_code=403, detail="Not allowed to view packets for this device")
    sensors = db.query(models.Sensor.id).filter(models.Sensor.device_id == device_id)
    return db.query(models.SensorPacket).filter(models.SensorPacket.sensor_id.in_(sensors)).all()
