from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.models import models
from datetime import datetime
import operator

def handle_new_measurement(session: Session, device_id, measured_data):
    """
    Called after a new measurement is inserted. Checks all alarms for the device and triggers if needed.
    """
    # Fetch all active alarms for this device and global alarms
    result = session.execute(
        select(models.Alarm).where(
            (models.Alarm.device_id == device_id) | (models.Alarm.global_ == True),
            models.Alarm.active == True
        )
    )
    alarms = result.scalars().all()
    for alarm in alarms:
        validate_alarm(session, alarm, measured_data, device_id)

def validate_alarm(session: Session, alarm, measured_data, device_id):
    """
    Validate a single alarm. If triggered, insert into TriggeredAlarm.
    """
    triggered = dynamic_validate_alarm(alarm, measured_data)
    if triggered:
        insert_triggered_alarm(session, alarm, device_id, measured_data)

def insert_triggered_alarm(session: Session, alarm, device_id, measured_data):
    from decimal import Decimal
    triggered_alarm = models.TriggeredAlarm(
        alarm_id=alarm.id,
        device_id=device_id,
        triggered_at=datetime.utcnow(),
        measured_value=Decimal(measured_data.get('value', 0))
    )
    session.add(triggered_alarm)
    session.commit()

# Dynamic validation function
ALARM_TYPE_CONFIG = {
    'consumo': {'measurement_key': 'energy_consumption', 'op': operator.gt},
    'tensao': {'measurement_key': 'voltage', 'op': operator.gt},
    'potencia': {'measurement_key': 'power', 'op': operator.gt},
    # Add more types here as needed
}

def dynamic_validate_alarm(alarm, measured_data):
    config = ALARM_TYPE_CONFIG.get(alarm.type)
    if not config:
        return False  # Unknown alarm type
    value = measured_data.get(config['measurement_key'], None)
    if value is None:
        return False
    try:
        return config['op'](float(value), float(alarm.threshold))
    except Exception:
        return False
