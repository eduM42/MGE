from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Numeric, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    owner = relationship('User', foreign_keys=[owner_id])
    users = relationship('User', back_populates='organization', foreign_keys='User.organization_id')
    devices = relationship('Device', back_populates='organization')
    alarms = relationship('Alarm', back_populates='organization')
    circuits = relationship('Circuit', back_populates='organization', foreign_keys='Circuit.organization_id')

class Circuit(Base):
    __tablename__ = 'circuits'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)  # NEW: user circuit
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True)  # NEW: org circuit
    user = relationship('User', back_populates='circuits', foreign_keys=[user_id])
    organization = relationship('Organization', back_populates='circuits', foreign_keys=[organization_id])
    devices = relationship('Device', back_populates='circuit')

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    is_residential = Column(Boolean, default=True, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True)
    organization = relationship('Organization', back_populates='users', foreign_keys=[organization_id])
    devices = relationship('Device', back_populates='user')
    alarms = relationship('Alarm', back_populates='user')
    device_access = relationship('UserDeviceAccess', back_populates='user')
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default='common_user')  # 'admin', 'org_owner', 'common_user'
    circuits = relationship('Circuit', back_populates='user', foreign_keys='Circuit.user_id')

class Device(Base):
    __tablename__ = 'devices'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pretty_name = Column(String(255), nullable=False)
    circuit_id = Column(UUID(as_uuid=True), ForeignKey('circuits.id', ondelete='SET NULL'), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    pending = Column(Boolean, default=True, nullable=False)  # New field
    circuit = relationship('Circuit', back_populates='devices')
    user = relationship('User', back_populates='devices')
    organization = relationship('Organization', back_populates='devices')
    sensors = relationship('Sensor', back_populates='device')
    residential_readings = relationship('ResidentialReading', back_populates='device')
    alarms = relationship('Alarm', back_populates='device')
    triggered_alarms = relationship('TriggeredAlarm', back_populates='device')
    device_access = relationship('UserDeviceAccess', back_populates='device')

class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'))
    type = Column(String(50), nullable=False)
    phase = Column(Integer)
    device = relationship('Device', back_populates='sensors')
    sensor_packets = relationship('SensorPacket', back_populates='sensor')

class ResidentialReading(Base):
    __tablename__ = 'residential_readings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'))
    timestamp = Column(DateTime, nullable=False)
    voltage = Column(Numeric(10,2))
    current = Column(Numeric(10,2))
    power = Column(Numeric(10,2))
    energy_consumption = Column(Numeric(10,2))
    device = relationship('Device', back_populates='residential_readings')

class SensorPacket(Base):
    __tablename__ = 'sensor_packets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey('sensors.id', ondelete='CASCADE'))
    received_at = Column(DateTime, default=datetime.utcnow)
    readings = Column(JSON, nullable=False)
    sensor = relationship('Sensor', back_populates='sensor_packets')

class Alarm(Base):
    __tablename__ = 'alarms'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)  # Added field
    threshold = Column(Numeric(10,2), nullable=False)
    type = Column(String(50), nullable=False)
    global_ = Column('global', Boolean, default=False, nullable=False)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    active = Column(Boolean, default=True, nullable=False)  # Added field
    device = relationship('Device', back_populates='alarms')
    organization = relationship('Organization', back_populates='alarms')
    user = relationship('User', back_populates='alarms')
    triggered_alarms = relationship('TriggeredAlarm', back_populates='alarm')

class TriggeredAlarm(Base):
    __tablename__ = 'triggered_alarms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    alarm_id = Column(UUID(as_uuid=True), ForeignKey('alarms.id', ondelete='CASCADE'))
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'))
    triggered_at = Column(DateTime, default=datetime.utcnow)
    measured_value = Column(Numeric(10,2), nullable=False)
    alarm = relationship('Alarm', back_populates='triggered_alarms')
    device = relationship('Device', back_populates='triggered_alarms')

class UserDeviceAccess(Base):
    __tablename__ = 'user_device_access'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'), primary_key=True)
    user = relationship('User', back_populates='device_access')
    device = relationship('Device', back_populates='device_access')
