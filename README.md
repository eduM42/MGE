# SGE Project

This project contains a Flask frontend and a FastAPI backend, both containerized for deployment.

## Structure

- `frontend/`: Flask application
- `backend/`: FastAPI application
- `docker-compose.yml`: Orchestrates both services

## Quick Start

1. Build and run with Docker Compose:
   ```powershell
   docker-compose up --build
   ```

2. Access the frontend at http://localhost:5000
3. The backend API will be available at http://localhost:8050

## Business Logic and Security

- **Authentication:**
  - JWT-based authentication is required for all backend routes except user registration and login.
  - Only authenticated users can access protected endpoints.

- **User Registration:**
  - Users register with a unique username and email.
  - Passwords are securely hashed.

- **Device Access Control:**
  - Users can only access devices they own (created) or have been explicitly granted access to via the user-device access table.
  - Only device owners can grant or revoke access to their devices for other users.
  - All device-related data (sensors, readings, packets, alarms, triggered alarms) is only accessible if the user owns the device or has been granted access.

- **CRUD Operations:**
  - Full CRUD is available for all main entities (organizations, circuits, users, devices, sensors, readings, packets, alarms, triggered alarms).
  - All CRUD operations are protected by authentication and device access rules as described above.

- **Special Queries:**
  - Endpoints are available to list devices, readings, packets, alarms, and triggered alarms by user, device, or organization, but always filtered by the current user's permissions.

- **User Permissions:**
  - Users can only view or manage their own access permissions and devices.
  - Users cannot view or manage other users' access unless they are the device owner.

## Notes

- The backend automatically creates and updates the database schema on startup (for development). For production, use Alembic for migrations.
- All API endpoints are documented and testable via the FastAPI docs at `/docs` (e.g., http://localhost:8050/docs).
