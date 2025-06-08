from pydantic import BaseModel, EmailStr, UUID4, Field, SecretStr
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal

# --- Organization ---
class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationRead(OrganizationBase):
    id: UUID4
    created_at: datetime
    class Config:
        from_attributes = True

# --- Circuit ---
class CircuitBase(BaseModel):
    name: str

class CircuitCreate(CircuitBase):
    pass

class CircuitRead(CircuitBase):
    id: UUID4
    class Config:
        from_attributes = True

# --- User ---
class UserBase(BaseModel):
    name: str
    username: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    is_residential: bool = True
    organization_id: Optional[UUID4] = None

class UserCreate(UserBase):
    password: SecretStr

class UserRead(UserBase):
    id: UUID4
    class Config:
        from_attributes = True

# --- Device ---
class DeviceBase(BaseModel):
    pretty_name: str
    circuit_id: Optional[UUID4] = None
    user_id: Optional[UUID4] = None
    organization_id: Optional[UUID4] = None
    pending: Optional[bool] = True

class DeviceCreate(DeviceBase):
    pass

class DeviceRegister(BaseModel):
    pretty_name: str
    username: str
    organization_name: Optional[str] = None

class DeviceRead(DeviceBase):
    id: UUID4
    created_at: datetime
    class Config:
        from_attributes = True

# --- Sensor ---
class SensorBase(BaseModel):
    device_id: UUID4
    type: str
    phase: Optional[int] = Field(None, ge=1, le=2)

class SensorCreate(SensorBase):
    pass

class SensorRead(SensorBase):
    id: UUID4
    class Config:
        from_attributes = True

# --- ResidentialReading ---
class ResidentialReadingBase(BaseModel):
    device_id: UUID4
    timestamp: datetime
    voltage: Optional[Decimal] = None
    current: Optional[Decimal] = None
    power: Optional[Decimal] = None
    energy_consumption: Optional[Decimal] = None

class ResidentialReadingCreate(ResidentialReadingBase):
    pass

class ResidentialReadingRead(ResidentialReadingBase):
    id: int
    class Config:
        from_attributes = True

# --- SensorPacket ---
class SensorPacketBase(BaseModel):
    device_id: UUID4
    readings: Any

class SensorPacketCreate(SensorPacketBase):
    pass

class SensorPacketRead(SensorPacketBase):
    id: int
    received_at: datetime
    class Config:
        from_attributes = True

# --- Alarm ---
class AlarmBase(BaseModel):
    name: str
    threshold: Decimal
    type: str
    global_: bool = Field(False, alias='global')
    device_id: Optional[UUID4] = None
    organization_id: Optional[UUID4] = None
    user_id: Optional[UUID4] = None

class AlarmCreate(AlarmBase):
    pass

class AlarmRead(AlarmBase):
    id: UUID4
    class Config:
        from_attributes = True
        validate_by_name = True

# --- TriggeredAlarm ---
class TriggeredAlarmBase(BaseModel):
    alarm_id: UUID4
    device_id: UUID4
    triggered_at: Optional[datetime] = None
    measured_value: Decimal

class TriggeredAlarmCreate(TriggeredAlarmBase):
    pass

class TriggeredAlarmRead(TriggeredAlarmBase):
    id: int
    class Config:
        from_attributes = True

# --- UserDeviceAccess ---
class UserDeviceAccessBase(BaseModel):
    user_id: UUID4
    device_id: UUID4

class UserDeviceAccessCreate(UserDeviceAccessBase):
    pass

class UserDeviceAccessRead(UserDeviceAccessBase):
    class Config:
        from_attributes = True
