from sqlalchemy.orm import Session
from . import models, database, auth

def create_admin_user():
    # Ensure tables exist
    models.Base.metadata.create_all(bind=database.engine)
    
    db = database.SessionLocal()
    try:
        # Check if admin exists
        user = db.query(models.User).filter(models.User.username == "admin").first()
        if not user:
            print("Creating admin user...")
            hashed_password = auth.get_password_hash("admin123")
            user = models.User(
                username="admin",
                email="admin@aegis.et",
                hashed_password=hashed_password,
                role=models.UserRole.SYS_ADMIN
            )
            db.add(user)
            db.commit()
            print("Admin user created: username='admin', password='admin123'")
        else:
            print("Admin user already exists.")

        # Seed essential agency roles
        seed_roles = {
            "command": models.UserRole.NATIONAL_SUPERVISOR,
            "police_cmd": models.UserRole.POLICE,
            "fire_cmd": models.UserRole.FIRE,
            "medical_cmd": models.UserRole.MEDICAL,
            "traffic_cmd": models.UserRole.TRAFFIC,
            "disaster_cmd": models.UserRole.DISASTER,
            "military_ops": models.UserRole.MILITARY,
            "verifier": models.UserRole.VERIFIER,
        }
        for username, role in seed_roles.items():
            if not db.query(models.User).filter(models.User.username == username).first():
                db.add(models.User(
                    username=username,
                    email=f"{username}@aegis.et",
                    hashed_password=auth.get_password_hash("changeme"),
                    role=role
                ))
        db.commit()

        # Seed Incidents
        if db.query(models.Incident).count() == 0:
            print("Seeding incidents...")
            incidents = [
                models.Incident(
                    title="Car Accident at Bole",
                    description="Two vehicle collision, blocking traffic.",
                    latitude=9.005401,
                    longitude=38.763611,
                    incident_type=models.IncidentType.ACCIDENT,
                    severity=models.IncidentSeverity.HIGH,
                    status=models.IncidentStatus.PENDING,
                    reporter_id=user.id
                ),
                models.Incident(
                    title="Fire in Piassa",
                    description="Small shop fire, smoke visible.",
                    latitude=9.030000,
                    longitude=38.750000,
                    incident_type=models.IncidentType.FIRE,
                    severity=models.IncidentSeverity.CRITICAL,
                    status=models.IncidentStatus.VERIFIED,
                    reporter_id=user.id
                ),
                models.Incident(
                    title="Flooding near Meskel Square",
                    description="Heavy rain caused drainage overflow.",
                    latitude=9.010000,
                    longitude=38.760000,
                    incident_type=models.IncidentType.HAZARD,
                    severity=models.IncidentSeverity.MEDIUM,
                    status=models.IncidentStatus.PENDING,
                    reporter_id=user.id
                )
            ]
            db.add_all(incidents)
            db.commit()
            print("Incidents seeded.")
        else:
            print("Incidents already exist.")

    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
