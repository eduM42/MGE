from fastapi import FastAPI
from .routers import auth, users, organizations, circuits, devices, sensors, residential_readings, sensor_packets, alarms, triggered_alarms, user_device_access

app = FastAPI(
    title="FastAPI Backend",
    description="A FastAPI backend for managing users and authentication.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(organizations.router)
app.include_router(circuits.router)
app.include_router(devices.router)
app.include_router(sensors.router)
app.include_router(residential_readings.router)
app.include_router(sensor_packets.router)
app.include_router(alarms.router)
app.include_router(triggered_alarms.router)
app.include_router(user_device_access.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend!"}
