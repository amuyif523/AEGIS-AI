from backend import models


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["database"] == "connected"
    assert body["status"] in ["healthy", "degraded"]


def test_incident_lifecycle(client):
    # Anonymous incident creation
    payload = {
        "title": "Test Incident",
        "description": "Fire near stadium",
        "latitude": 9.0,
        "longitude": 38.7,
        "incident_type": models.IncidentType.FIRE.value,
        "severity": models.IncidentSeverity.HIGH.value,
    }
    create_resp = client.post("/incidents/", json=payload)
    assert create_resp.status_code == 200
    incident = create_resp.json()
    assert incident["status"] == models.IncidentStatus.PENDING.value
    assert incident["incident_type"] in models.IncidentType._value2member_map_
    assert incident["severity"] in models.IncidentSeverity._value2member_map_

    # Listing incidents returns the new one
    list_resp = client.get("/incidents/")
    assert list_resp.status_code == 200
    ids = [i["id"] for i in list_resp.json()]
    assert incident["id"] in ids
