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
    assert incident["source"] == models.IncidentSource.CITIZEN.value
    assert incident["verified_by_id"] is None
    assert incident["resolved_by_id"] is None
    assert "ai_confidence" in incident
    assert "escalation_probability" in incident
    assert "spread_risk" in incident
    assert "casualty_likelihood" in incident
    assert "suggested_agencies" in incident
    assert "suggested_unit_type" in incident

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


def test_status_transition_audit(client):
    db = next(get_db())
    admin = create_user(db, "sysadmin1", models.UserRole.SYS_ADMIN)
    token_resp = client.post(
        "/token",
        data={"username": admin.username, "password": "testpass"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]

    incident_resp = client.post(
        "/incidents/",
        json={
            "title": "Fire Test",
            "description": "Smoke visible",
            "latitude": 1.1,
            "longitude": 2.2,
            "incident_type": models.IncidentType.FIRE.value,
            "severity": models.IncidentSeverity.HIGH.value,
        },
    )
    incident_id = incident_resp.json()["id"]

    verify_resp = client.patch(
        f"/incidents/{incident_id}?status=verified",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert verify_resp.status_code == 200
    body = verify_resp.json()
    assert body["verified_by_id"] == admin.id
    assert body["verified_at"] is not None

    resolve_resp = client.patch(
        f"/incidents/{incident_id}?status=resolved",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resolve_resp.status_code == 200

    back_resp = client.patch(
        f"/incidents/{incident_id}?status=pending",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert back_resp.status_code == 400


def test_dedup_sets_potential_duplicate(client):
    # Create first incident
    first_resp = client.post(
        "/incidents/",
        json={
            "title": "Same Title",
            "description": "Smoke visible",
            "latitude": 1.0,
            "longitude": 1.0,
            "incident_type": models.IncidentType.FIRE.value,
            "severity": models.IncidentSeverity.MEDIUM.value,
        },
    )
    first_id = first_resp.json()["id"]

    # Create second nearby with same title
    second_resp = client.post(
        "/incidents/",
        json={
            "title": "Same Title",
            "description": "Another report",
            "latitude": 1.0001,
            "longitude": 1.0001,
            "incident_type": models.IncidentType.FIRE.value,
            "severity": models.IncidentSeverity.MEDIUM.value,
        },
    )
    assert second_resp.status_code == 200
    body = second_resp.json()
    assert body["potential_duplicate_id"] == first_id


def test_bbox_and_near_queries(client):
    # Seed two incidents
    client.post(
        "/incidents/",
        json={
            "title": "BBox A",
            "description": "Test",
            "latitude": 1.0,
            "longitude": 1.0,
            "incident_type": models.IncidentType.FIRE.value,
            "severity": models.IncidentSeverity.LOW.value,
        },
    )
    client.post(
        "/incidents/",
        json={
            "title": "BBox B",
            "description": "Test",
            "latitude": 10.0,
            "longitude": 10.0,
            "incident_type": models.IncidentType.FIRE.value,
            "severity": models.IncidentSeverity.LOW.value,
        },
    )

    bbox_resp = client.get("/incidents/bbox?min_lat=0&max_lat=2&min_lng=0&max_lng=2")
    assert bbox_resp.status_code == 200
    assert len(bbox_resp.json()) >= 1

    near_resp = client.get("/incidents/near?lat=1&lng=1&radius_km=50")
    assert near_resp.status_code == 200
    assert len(near_resp.json()) >= 1


def test_nearest_unit_and_proximity_alerts(client):
    db = next(get_db())
    u = models.Unit(
        callsign="TEST-UNIT",
        unit_type=models.UserRole.MEDICAL,
        status=models.UnitStatus.IDLE,
        latitude=1.0,
        longitude=1.0,
    )
    db.add(u)
    db.commit()
    db.refresh(u)

    incident_resp = client.post(
        "/incidents/",
        json={
            "title": "Critical Medical",
            "description": "Severe injury",
            "latitude": 1.0,
            "longitude": 1.0,
            "incident_type": models.IncidentType.MEDICAL.value,
            "severity": models.IncidentSeverity.CRITICAL.value,
        },
    )
    assert incident_resp.status_code == 200

    prox = client.get("/routing/proximity_alerts?lat=1&lng=1&radius_km=1")
    assert prox.status_code == 200
    assert len(prox.json()) >= 1

    nearest = client.get("/routing/nearest_unit?lat=1&lng=1&unit_type=medical")
    assert nearest.status_code == 200
    body = nearest.json()
    assert body["unit_id"] == u.id
