# AEGIS-AI: Geospatial Incident Intelligence Platform

## Overview
AEGIS-AI is a national-scale, AI-assisted incident intelligence and rapid response stack. It currently ships a FastAPI backend with role-based auth, incidents/units/alerts, a React + Leaflet dashboard, and WebSocket-driven refresh hooks.

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy, Postgres/PostGIS (dev fallback: SQLite), Alembic migrations, JWT auth
- **Frontend:** React 18, Vite, Tailwind, Leaflet
- **Tooling:** Docker Compose profiles (dev/prod), pytest + TestClient, Vitest + RTL

## Setup
1) Copy env template and adjust credentials/URLs:
```bash
cp .env.example .env
```

2) Backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3) Frontend dependencies:
```bash
cd frontend
npm install
```

## Database & Migrations
- Configure `DATABASE_URL` in `.env` (default Postgres, falls back to local SQLite).
- Run migrations:
```bash
cd backend
alembic upgrade head
```
- Optional seed (dev convenience; creates sys_admin plus core agency users with password `changeme` and sample incidents):
```bash
python -m backend.seed_data
```

## Running
- **Backend (local):**
```bash
cd backend
uvicorn main:app --reload
```
- **Frontend (local):**
```bash
cd frontend
npm run dev
```
- **Docker Compose:**
  - Dev profile (mounted code, reload): `docker compose --profile dev up --build`
  - Prod profile (no mounts): `docker compose --profile prod up --build`

## RBAC (Sprint 1 expansion)
- Core roles: `citizen`, `verifier`, `police`, `medical`, `fire`, `traffic`, `disaster_coordinator`, `military_analyst`, `national_supervisor`, `command` (legacy), `admin` (legacy), `sys_admin`.
- Admin-capable (user/unit management, alerts): `sys_admin`, `national_supervisor`, `admin`, `command`.
- Dispatch-capable (incident status/assign): admin-capable plus `police`, `fire`, `medical`, `traffic`, `disaster_coordinator`, `military_analyst`.

## Incident Model (current)
- Fields: title, description, latitude/longitude, incident_type, severity, status, source, media_url/media_type, flag_reason, duplicate links, AI signals (ai_confidence, escalation_probability, spread_risk, casualty_likelihood, crowd_size_estimate).
- Audit: reporter_id, verified/dispatched/resolved timestamps and by-user IDs, assigned_unit_id, flagged_by.
- Workflow: pending → verified → dispatched → resolved/false_alarm (invalid transitions rejected); merge/flag endpoints for verifiers/admins.
- Attachments: incident attachments with url/media_type/metadata.
- Routing: suggested_agencies, suggested_unit_type, routing_rationale populated from triage.
- GIS queries: `/incidents/near` (radius km) and `/incidents/bbox`; geometry stored for Postgres with spatial index; static base layers at `/layers/base`.

## Testing
- Backend: `cd backend && pytest`
- Frontend: `cd frontend && npm run test`

## Project Structure
- `backend/` – API, models, auth, Alembic migrations (`alembic/`), tests
- `frontend/` – React app, components, Vitest setup
- `docker-compose.yml` – dev/prod profiles with PostGIS
- `.env.example` – configuration template
