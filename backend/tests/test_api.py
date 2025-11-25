from backend import models
from backend.auth import get_password_hash
from backend.database import get_db
from backend.main import app


def create_user(db, username: str, role: models.UserRole, password: str = "testpass"):
    user = models.User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=get_password_hash(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


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


def test_rbac_blocks_dispatch_for_citizen(client):
    # Create a citizen and login
    db = next(get_db())
    citizen = create_user(db, "citizen1", models.UserRole.CITIZEN)
    token_resp = client.post(
        "/token",
        data={"username": citizen.username, "password": "testpass"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]

    # Create incident anonymously
    incident_resp = client.post(
        "/incidents/",
        json={
            "title": "Blocked Road",
            "description": "Traffic jam",
            "latitude": 1.0,
            "longitude": 1.0,
            "incident_type": models.IncidentType.ACCIDENT.value,
            "severity": models.IncidentSeverity.MEDIUM.value,
        },
    )
    incident_id = incident_resp.json()["id"]

    # Citizen tries to update status -> forbidden
    update_resp = client.patch(
        f"/incidents/{incident_id}?status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_resp.status_code == 403
