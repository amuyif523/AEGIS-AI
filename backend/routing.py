from typing import List, Dict
from . import models

# Map incident types to preferred roles/unit types
ROUTING_TABLE: Dict[models.IncidentType, List[models.UserRole]] = {
    models.IncidentType.FIRE: [models.UserRole.FIRE, models.UserRole.DISASTER],
    models.IncidentType.FLOOD: [models.UserRole.DISASTER, models.UserRole.TRAFFIC],
    models.IncidentType.ACCIDENT: [models.UserRole.TRAFFIC, models.UserRole.MEDICAL],
    models.IncidentType.MEDICAL: [models.UserRole.MEDICAL],
    models.IncidentType.CRIME: [models.UserRole.POLICE],
    models.IncidentType.UNREST: [models.UserRole.POLICE, models.UserRole.MILITARY],
    models.IncidentType.HAZARD: [models.UserRole.FIRE, models.UserRole.DISASTER],
    models.IncidentType.INFRASTRUCTURE: [models.UserRole.DISASTER, models.UserRole.TRAFFIC],
    models.IncidentType.CROWD: [models.UserRole.POLICE, models.UserRole.TRAFFIC],
    models.IncidentType.SUSPICIOUS: [models.UserRole.POLICE],
    models.IncidentType.OTHER: [models.UserRole.DISASTER, models.UserRole.POLICE],
}


def suggest_agencies(incident_type: models.IncidentType, severity: models.IncidentSeverity) -> List[models.UserRole]:
    """
    Suggest agencies based on incident type and severity.
    High/critical can escalate to command/national_supervisor.
    """
    roles = ROUTING_TABLE.get(incident_type, [models.UserRole.POLICE])
    if severity in [models.IncidentSeverity.HIGH, models.IncidentSeverity.CRITICAL]:
        roles = roles + [models.UserRole.COMMAND, models.UserRole.NATIONAL_SUPERVISOR]
    # Remove duplicates while preserving order
    seen = set()
    deduped = []
    for r in roles:
        if r not in seen:
            seen.add(r)
            deduped.append(r)
    return deduped


def suggest_unit_type(incident_type: models.IncidentType) -> models.UserRole:
    """
    Suggest a unit type for dispatch based on incident type.
    """
    mapping = {
        models.IncidentType.FIRE: models.UserRole.FIRE,
        models.IncidentType.FLOOD: models.UserRole.DISASTER,
        models.IncidentType.ACCIDENT: models.UserRole.MEDICAL,
        models.IncidentType.MEDICAL: models.UserRole.MEDICAL,
        models.IncidentType.CRIME: models.UserRole.POLICE,
        models.IncidentType.UNREST: models.UserRole.POLICE,
        models.IncidentType.HAZARD: models.UserRole.FIRE,
        models.IncidentType.INFRASTRUCTURE: models.UserRole.DISASTER,
        models.IncidentType.CROWD: models.UserRole.POLICE,
        models.IncidentType.SUSPICIOUS: models.UserRole.POLICE,
    }
    return mapping.get(incident_type, models.UserRole.POLICE)


def build_routing_rationale(incident: models.Incident, suggested_roles: List[models.UserRole], suggested_unit: models.UserRole) -> str:
    parts = [
        f"type={incident.incident_type.value}",
        f"severity={incident.severity.value}",
        f"agencies={','.join([r.value for r in suggested_roles])}",
        f"suggested_unit_type={suggested_unit.value}",
    ]
    return "; ".join(parts)
