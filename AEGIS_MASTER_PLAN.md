# AEGIS-AI Master Plan
AI-enhanced geospatial incident intelligence and multi-agency response for Ethiopian urban environments.

## Current Status
- Sprint 0 — Foundations: done (env/config/logging, health checks, Alembic, dev/prod compose, backend/frontend test scaffolds).
- Sprint 1 — RBAC expansion: done (expanded roles, guards, seed users, docs).

## Roadmap (right-sized, in order)
2) Intake Core
   - Citizen/field/ops-center reporting endpoints with geometry, media metadata, audit fields.
   - Status workflow: pending → verified → dispatched → resolved/false alarm; WebSocket events.

3) Verification & Media
   - Attachments (photo/file metadata), basic deduping (geo/time/text), verifier role flow.
   - Admin tools: approve/flag/merge incidents; audit trails.

4) AI Triage v1
   - 12+ class classifier + severity scoring (Amharic + English heuristics/model stub).
   - Confidence + escalation probability exposed in API; risk cues (spread/casualty/crowd) as heuristics.

5) Routing Logic
   - Agency/unit routing rules per class/severity/location; suggested unit types.
   - Prepare interfaces for future model-based routing; surface rationale in responses.

6) GIS Data Plane
   - PostGIS geometries + spatial indexes; queries (radius, bbox, boundary).
   - Base layers: admin boundaries, police/fire districts, hospitals, hydrants, critical infra, road network, water/flood zones, weather overlay stubs.

7) Map UX & Clustering
   - Frontend layers/filters, severity styling, clustering/heatmaps, buffer/proximity tools, timeline slider.
   - Caching of incidents/layers for resilience.

8) Routing & Proximity Alerts
   - Nearest-unit lookup; route suggestions (shortest/fastest) with congestion stub.
   - Radius/proximity alerts for citizens/responders; spatial risk index per incident.

9) Agency Dashboards — Policing
   - Crime/unrest layers, patrol/jurisdiction overlays, crowd mapping; filtered queues and actions per role.

10) Agency Dashboards — Safety/Disaster
   - Medical: hospital proximity/capacity, ambulance routing, triage queue.
   - Fire: fire-risk layers, hydrants, building density; spread indicators.
   - Traffic: congestion/closures, rerouting, incident impact on network.
   - Disaster: weather/flood/landslide zones, evacuation routes, shelters.

11) Command & Alerting Engine
   - Command/National view: consolidated multi-agency status, escalated events.
   - GIS-targeted alerts with severity + distance + recommended action; multi-agency briefings, evacuation/proximity warnings.

12) Mission Threads & Collaboration
   - Incident chats/notes/attachments per agency; mission threads grouping related incidents.
   - Shared map annotations (roadblocks, safe zones, staging areas) with permissions.

13) Analytics Dashboards
   - Incident density maps, weekly/monthly spatial trends, severity distribution, response time stats.
   - Agency performance dashboards; exports (CSV/PDF).

14) Offline/Low-Bandwidth + Localization
   - PWA, map tile caching, retry queues, compressed uploads.
   - Amharic/English UI, localized dates/numbers; accessibility/error UX.

15) Predictive/Forecasting (optional/academic)
   - Crime/fire/flood risk overlays; crowd density estimation; unrest pattern stub.

## Principles
- GIS-first (PostGIS, spatial indexes by default); AI-pluggable with confidence/rationale.
- Role-aware and jurisdiction-scoped; real-time via WebSockets/bus.
- Offline-tolerant for low-bandwidth contexts; localization built-in.
