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
- Optional seed (dev convenience):
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

## Testing
- Backend: `cd backend && pytest`
- Frontend: `cd frontend && npm run test`

## Project Structure
- `backend/` – API, models, auth, Alembic migrations (`alembic/`), tests
- `frontend/` – React app, components, Vitest setup
- `docker-compose.yml` – dev/prod profiles with PostGIS
- `.env.example` – configuration template
