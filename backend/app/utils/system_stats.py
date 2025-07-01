import platform
import psutil
from sqlalchemy.orm import Session
from app.models import models

def get_system_statistics(db: Session):
    # System info
    system_info = {
        'kernel': platform.release(),
        'uptime': str(psutil.boot_time()),
        'num_cores': psutil.cpu_count(),
        'cpu_architecture': platform.machine(),
        'cpu_type': platform.processor(),
        'active_alarms': db.query(models.Alarm).filter(models.Alarm.active == True).count(),
        'triggered_alarms': db.query(models.TriggeredAlarm).count(),
        'active_devices': db.query(models.Device).filter(models.Device.pending == False).count(),
    }
    # Table counts
    database_tables = []
    for table in [models.User, models.Device, models.Alarm, models.TriggeredAlarm, models.Organization, models.Circuit]:
        database_tables.append({
            'name': table.__tablename__,
            'record_count': db.query(table).count()
        })
    # Processes
    processes = [{'pid': p.pid, 'name': p.name()} for p in psutil.process_iter(['pid', 'name'])][:20]
    return {
        'system_info': system_info,
        'database_tables': database_tables,
        'processes': processes
    }
