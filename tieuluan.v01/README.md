# Healthcare Microservices with PostgreSQL and Web UI

This project now includes:

- Patient Service with PostgreSQL
- Doctor Service with PostgreSQL
- Appointment Service with PostgreSQL
- Appointment dependency validation via API calls to Patient and Doctor services
- Healthcare-inspired web UI for booking appointments
- Login with role-based authorization (patient or staff)

Design note:

- UI visual direction is inspired by modern healthcare platforms (for example Mayo Clinic style language), but implemented as an original interface.

## 1) Architecture

- Patient Service: manages patient records
- Doctor Service: manages doctor records and specialties
- Appointment Service: books appointments and validates patient_id and doctor_id by calling other services
- Frontend: static web app that consumes all 3 APIs
- PostgreSQL: one instance, database-per-service setup

Databases:

- patient_db
- doctor_db
- appointment_db

## 2) Run with Docker

```bash
docker compose -f docker-compose.microservices.yml up --build
```

Endpoints:

- UI: http://localhost:8080
- Patient API docs: http://localhost:8001/docs
- Doctor API docs: http://localhost:8002/docs
- Appointment API docs: http://localhost:8003/docs

## 2.1) Demo login accounts

- staff / staff123
- patient1 / patient123 (mapped to patient_id=1)
- patient2 / patient123 (mapped to patient_id=2)

Token flow:

- UI calls `POST /auth/login` on Appointment Service to get JWT token
- UI attaches `Authorization: Bearer <token>` for all API calls

Role rules:

- staff: can list all patients, create patients, and create appointments for any patient
- patient: can read only self profile and create appointments only for self

## 3) API examples

Create patient:

```bash
curl -X POST http://localhost:8001/patients \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Le Van C","age":30,"phone":"0903000111"}'
```

Create doctor:

```bash
curl -X POST http://localhost:8002/doctors \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Dr. Nguyen K","specialty":"Neurology"}'
```

Create appointment (depends on existing patient and doctor):

```bash
curl -X POST http://localhost:8003/appointments \
  -H "Content-Type: application/json" \
  -d '{"patient_id":1,"doctor_id":1,"appointment_time":"2026-04-26T09:00:00Z","reason":"General consultation"}'
```

Login to get token:

```bash
curl -X POST http://localhost:8003/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"staff","password":"staff123"}'
```

## 4) Service files

- services/patient_service/main.py
- services/doctor_service/main.py
- services/appointment_service/main.py
- services/db/init-microservices.sql
- services/frontend/index.html
- services/frontend/styles.css
- services/frontend/app.js