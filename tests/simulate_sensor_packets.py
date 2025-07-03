import requests
import uuid
import random
import json
import math
from datetime import datetime

BACKEND_URL = "http://localhost:8050"  # Adjust if needed

def get_token():
    print("Login required.")
    username = input("Username: ")
    password = input("Password: ")
    resp = requests.post(f"{BACKEND_URL}/auth/token", data={
        "username": username,
        "password": password
    })
    if resp.status_code == 200:
        return resp.json()["access_token"]
    else:
        print("Login failed! Status:", resp.status_code)
        print(resp.text)
        exit(1)

def api_get(path, token):
    resp = requests.get(f"{BACKEND_URL}{path}", headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 401:
        print("Unauthorized. Check your credentials.")
        exit(1)
    resp.raise_for_status()
    return resp

def api_post(path, data, token):
    resp = requests.post(f"{BACKEND_URL}{path}", json=data, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 401:
        print("Unauthorized. Check your credentials.")
        exit(1)
    return resp

def get_devices(token):
    resp = api_get("/devices/", token)
    return resp.json()

def get_sensors(device_id, sensor_type, token):
    resp = api_get(f"/sensors/by_device/{device_id}", token)
    sensors = resp.json()
    return [s for s in sensors if s['type'] == sensor_type]

def main():
    print("=== Simulate Sensor Packets ===")
    token = get_token()
    devices = get_devices(token)
    if not devices:
        print("No devices found in backend.")
        return
    print("Available devices:")
    for idx, d in enumerate(devices):
        print(f"{idx+1}: {d['pretty_name']} (ID: {d['id']})")
    device_idx = int(input("Select device by number: ")) - 1
    device = devices[device_idx]
    voltage_sensors = get_sensors(device['id'], 'voltage', token)
    current_sensors = get_sensors(device['id'], 'current', token)
    if not voltage_sensors or not current_sensors:
        print("Device must have both voltage and current sensors.")
        return
    voltage_sensor = voltage_sensors[0]
    current_sensor = current_sensors[0]
    print(f"Selected voltage sensor: {voltage_sensor['id']}")
    print(f"Selected current sensor: {current_sensor['id']}")
    # Simulate readings
    n_packets = int(input("How many packets to send? (default 1): ") or "1")
    # Prompt for phase shift in degrees
    phase_shift_deg = float(input("Enter phase shift for current (degrees, e.g. 0 for in-phase, 45 for lower power factor, 90 for minimum real power): ") or "0")
    phase_shift_rad = math.radians(phase_shift_deg)
    for i in range(n_packets):
        # Generate sine wave for voltage: -179V to 179V (peak-to-peak)
        v_values = [179 * math.sin(2 * math.pi * x / 500) for x in range(500)]
        # Generate sine wave for current: -1A to 1A (peak-to-peak), with phase shift
        i_values = [1 * math.sin(2 * math.pi * x / 500 + phase_shift_rad) for x in range(500)]
        now = datetime.utcnow().isoformat()
        v_packet = {
            "sensor_id": voltage_sensor['id'],
            # "received_at": now,
            "readings": {"values": v_values}
        }
        i_packet = {
            "sensor_id": current_sensor['id'],
            # "received_at": now,
            "readings": {"values": i_values}
        }
        print(f"Sending voltage packet {i+1}...")
        v_resp = api_post("/sensor_packets/", v_packet, token)
        print(f"Voltage packet status: {v_resp.status_code}\n Message: {v_resp.text}")
        print(f"Sending current packet {i+1}...")
        i_resp = api_post("/sensor_packets/", i_packet, token)
        print(f"Current packet status: {i_resp.status_code}\n Message: {i_resp.text}")
    print("Done. Check backend for stored measurements.")

if __name__ == "__main__":
    main()
