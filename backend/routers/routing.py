from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, database
from math import radians, sin, cos, sqrt, atan2

router = APIRouter(prefix="/routing", tags=["routing"])


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


@router.get("/nearest_unit")
def nearest_unit(lat: float, lng: float, unit_type: models.UserRole | None = None, db: Session = Depends(database.get_db)):
    units = db.query(models.Unit).filter(models.Unit.status == models.UnitStatus.IDLE).all()
    if unit_type:
        units = [u for u in units if u.unit_type == unit_type]
    if not units:
        raise HTTPException(status_code=404, detail="No idle units found")
    scored = []
    for u in units:
        if u.latitude is None or u.longitude is None:
            continue
        distance_km = haversine(lat, lng, u.latitude, u.longitude)
        # Simple congestion stub: add 10% if distance > 10km
        eta_min = distance_km / 0.5 * 1.1 if distance_km > 10 else distance_km / 0.5
        scored.append((distance_km, eta_min, u))
    if not scored:
        raise HTTPException(status_code=404, detail="No locatable units")
    scored.sort(key=lambda x: x[0])
    distance_km, eta_min, unit = scored[0]
    return {
        "unit_id": unit.id,
        "callsign": unit.callsign,
        "unit_type": unit.unit_type,
        "distance_km": distance_km,
        "eta_minutes": eta_min,
    }


@router.get("/proximity_alerts")
def proximity_alerts(lat: float, lng: float, radius_km: float = 5.0, db: Session = Depends(database.get_db)):
    incidents = db.query(models.Incident).all()
    alerts = []
    for inc in incidents:
        d = haversine(lat, lng, inc.latitude, inc.longitude)
        if d <= radius_km and inc.severity in [models.IncidentSeverity.HIGH, models.IncidentSeverity.CRITICAL]:
            alerts.append({
                "incident_id": inc.id,
                "title": inc.title,
                "severity": inc.severity,
                "distance_km": d,
                "recommended_action": "Avoid area" if inc.incident_type in [models.IncidentType.UNREST, models.IncidentType.CRIME] else "Seek shelter",
                "spatial_risk_index": inc.spatial_risk_index or 0,
            })
    return alerts
