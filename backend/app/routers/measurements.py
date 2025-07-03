from fastapi import APIRouter, Depends, Body, Response
from sqlalchemy.orm import Session
from app.models import models
from app.database import get_db
from app.utils.measurement_calcs import calculate_rms, calculate_power, calculate_power_factor
from datetime import timedelta, datetime
import io, csv, json
import pandas as pd

router = APIRouter(prefix="/measurements", tags=["measurements"])

@router.post("/process_latest")
def process_latest_measurements(db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    for device in devices:
        voltage_sensor = db.query(models.Sensor).filter_by(device_id=device.id, type='voltage').first()
        current_sensor = db.query(models.Sensor).filter_by(device_id=device.id, type='current').first()
        if not voltage_sensor or not current_sensor:
            continue
        v_packet = db.query(models.SensorPacket).filter_by(sensor_id=voltage_sensor.id).order_by(models.SensorPacket.received_at.desc()).first()
        i_packet = db.query(models.SensorPacket).filter_by(sensor_id=current_sensor.id).order_by(models.SensorPacket.received_at.desc()).first()
        if not v_packet or not i_packet:
            continue
        if abs((v_packet.received_at - i_packet.received_at).total_seconds()) > 1:
            continue
        v_values = v_packet.readings.get("values", [])
        i_values = i_packet.readings.get("values", [])
        if len(v_values) != 500 or len(i_values) != 500:
            continue
        voltage_rms = calculate_rms(v_values)
        current_rms = calculate_rms(i_values)
        power = calculate_power(voltage_rms, current_rms)
        power_factor = calculate_power_factor(v_values, i_values)
        energy_increment = power / 3600
        reading = models.ResidentialReading(
            device_id=device.id,
            timestamp=v_packet.received_at,
            voltage=voltage_rms,
            current=current_rms,
            power=power,
            energy_consumption=energy_increment,
            power_factor=power_factor  # Store power factor
        )
        db.add(reading)
        db.commit()
    return {"status": "processed"}

@router.post("/export")
def export_measurements(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    file_format = data.get('file_format', 'csv')
    timeframe = data.get('timeframe', 'last_24h')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    devices = data.get('devices', [])
    measurements = data.get('measurements', ['power', 'voltage', 'current', 'consumption'])

    # Timeframe logic
    now = datetime.utcnow()
    if timeframe == 'last_24h':
        start = now - timedelta(days=1)
        end = now
    elif timeframe == 'last_7d':
        start = now - timedelta(days=7)
        end = now
    elif timeframe == 'last_30d':
        start = now - timedelta(days=30)
        end = now
    elif timeframe == 'custom' and start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        start = now - timedelta(days=1)
        end = now

    # Query readings
    query = db.query(models.ResidentialReading)
    if devices and 'all' not in devices:
        query = query.filter(models.ResidentialReading.device_id.in_(devices))
    query = query.filter(models.ResidentialReading.timestamp >= start, models.ResidentialReading.timestamp <= end)
    readings = query.all()

    # Prepare data
    rows = []
    for r in readings:
        row = {
            'device_id': str(r.device_id),
            'timestamp': r.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if 'power' in measurements:
            row['power'] = float(r.power) if r.power is not None else None
        if 'voltage' in measurements:
            row['voltage'] = float(r.voltage) if r.voltage is not None else None
        if 'current' in measurements:
            row['current'] = float(r.current) if r.current is not None else None
        if 'consumption' in measurements:
            row['consumption'] = float(r.energy_consumption) if r.energy_consumption is not None else None
        if 'power_factor' in measurements:
            row['power_factor'] = float(r.power_factor) if hasattr(r, 'power_factor') and r.power_factor is not None else None
        rows.append(row)

    # Export
    if file_format == 'csv':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys() if rows else ['device_id','timestamp'])
        writer.writeheader()
        writer.writerows(rows)
        return Response(content=output.getvalue(), media_type='text/csv', headers={"Content-Disposition": "attachment; filename=export.csv"})
    elif file_format == 'xlsx':
        df = pd.DataFrame(rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return Response(content=output.read(), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={"Content-Disposition": "attachment; filename=export.xlsx"})
    elif file_format == 'json':
        return Response(content=json.dumps(rows, ensure_ascii=False), media_type='application/json', headers={"Content-Disposition": "attachment; filename=export.json"})
    else:
        return Response(content='Formato não suportado', status_code=400)
