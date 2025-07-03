import requests
from flask import session

BACKEND_URL = "http://backend:8050"  # Use 'http://localhost:8050' for local dev if needed

def get_token():
    return session.get('access_token')

def get_headers():
    token = get_token()
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}

def api_post(path, data=None, json=None, stream=False):
    url = f"{BACKEND_URL}{path}"
    headers = get_headers()
    return requests.post(url, data=data, json=json, headers=headers, stream=stream)

def api_get(path, params=None):
    url = f"{BACKEND_URL}{path}"
    headers = get_headers()
    return requests.get(url, params=params, headers=headers)

def api_put(path, data=None, json=None):
    url = f"{BACKEND_URL}{path}"
    headers = get_headers()
    return requests.put(url, data=data, json=json, headers=headers)

def api_delete(path):
    url = f"{BACKEND_URL}{path}"
    headers = get_headers()
    return requests.delete(url, headers=headers)

def api_patch(path, data=None, json=None):
    url = f"{BACKEND_URL}{path}"
    headers = get_headers()
    return requests.patch(url, data=data, json=json, headers=headers)

# --- Sensor Management Helpers ---
def get_user_devices(user_id):
    # Returns devices the user owns or has access to (uses /devices/ endpoint)
    resp = api_get(f"/devices/")
    if resp.ok:
        return resp.json()
    return []

def get_user_sensors(user_id):
    # Returns all sensors for devices the user can access
    devices = get_user_devices(user_id)
    sensors = []
    for device in devices:
        resp = api_get(f"/sensors/by_device/{device['id']}")
        if resp.ok:
            sensors.extend(resp.json())
    # Attach device info to each sensor for display
    for sensor in sensors:
        for device in devices:
            if sensor.get('device_id') == device.get('id'):
                sensor['device'] = device
    return sensors

def add_sensor(device_id, sensor_type, phase):
    data = {"device_id": device_id, "type": sensor_type, "phase": int(phase)}
    resp = api_post("/sensors/", json=data)
    if resp.ok:
        return {"success": True, "sensor": resp.json()}
    else:
        try:
            error = resp.json().get('detail', 'Unknown error')
        except Exception:
            error = resp.text
        return {"success": False, "error": error}

def delete_sensor(sensor_id):
    resp = api_delete(f"/sensors/{sensor_id}")
    return resp.ok
