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

## Docker Deployment

This project is fully containerized. To build and run both the frontend and backend, use:

```powershell
docker-compose up --build
```

- The Flask frontend will be available at: http://localhost:5000
- The FastAPI backend API will be available at: http://localhost:8050

You can stop the stack with:

```powershell
docker-compose down
```

### Development Notes
- Code changes in `frontend/app` and `backend/app` are automatically reflected in the running containers (volumes are mounted).
- The backend uses a SQLite database by default (`backend/app/test.db`).

## Default User (Lab Configuration)

On first startup, the backend will automatically create a default admin user:

- **Username:** `admin`
- **Password:** `admin`
- **Email:** `admin@example.com`

> ⚠️ **Change the default password in production!**

You can log in with these credentials at the frontend login page. This user has full administrative privileges.

## API Documentation

The backend provides interactive API docs at:
- http://localhost:8050/docs (Swagger UI)
- http://localhost:8050/redoc (ReDoc)
