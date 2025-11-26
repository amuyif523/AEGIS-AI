import logging
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List
from datetime import timedelta, datetime

from . import models, schemas, database, auth
from .ai_engine import ai_engine
from .config import get_settings
from .rbac import admin_roles, dispatcher_roles, require_roles

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("aegis")

# Create Database Tables (Simple auto-migration for MVP)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="AEGIS-AI National Intelligence API",
    description="Real-time geospatial incident management and AI triage system.",
    version="1.0.0"
)

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def read_root():
    return {
        "system": "AEGIS-AI", 
        "status": "operational", 
        "layer": "National Intelligence Core",
        "version": "1.0.0"
    }

# --- User Endpoints ---

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    # Force role to CITIZEN for public registration
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password, role=models.UserRole.CITIZEN)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/admin/users/", response_model=schemas.UserResponse)
def create_user_admin(user: schemas.UserCreateAdmin, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_admin)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# --- Unit Endpoints ---

@app.get("/units/", response_model=List[schemas.UnitResponse])
def read_units(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    units = db.query(models.Unit).offset(skip).limit(limit).all()
    return units

@app.post("/units/", response_model=schemas.UnitResponse)
def create_unit(unit: schemas.UnitCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_admin)):
    db_unit = models.Unit(**unit.model_dump())
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit

@app.patch("/units/{unit_id}", response_model=schemas.UnitResponse)
def update_unit(unit_id: int, unit_update: schemas.UnitUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Only Admin/Command or the unit itself (future) can update status
    if current_user.role not in admin_roles + [models.UserRole.DISASTER, models.UserRole.TRAFFIC]:
        raise HTTPException(status_code=403, detail="Not authorized to update unit status")

    db_unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if not db_unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    update_data = unit_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_unit, key, value)
    
    db.commit()
    db.refresh(db_unit)
    return db_unit

# --- Incident Endpoints ---

@app.post("/incidents/", response_model=schemas.IncidentResponse)
def create_incident(incident: schemas.IncidentCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user_optional)):
    # Determine reporter ID
    if current_user:
        reporter_id = current_user.id
    else:
        # Fallback to "citizen_zero" for anonymous reports
        citizen_zero = db.query(models.User).filter(models.User.username == "citizen_zero").first()
        if not citizen_zero:
             # Create citizen_zero if not exists
            citizen_zero = models.User(username="citizen_zero", email="anonymous@aegis.et", hashed_password="hash", role=models.UserRole.CITIZEN)
            db.add(citizen_zero)
            db.commit()
            db.refresh(citizen_zero)
        reporter_id = citizen_zero.id

    # Determine source based on caller
    source = incident.source
    if current_user:
        if current_user.role in admin_roles:
            source = models.IncidentSource.OPS_CENTER
        elif current_user.role in [
            models.UserRole.POLICE,
            models.UserRole.FIRE,
            models.UserRole.MEDICAL,
            models.UserRole.TRAFFIC,
            models.UserRole.DISASTER,
            models.UserRole.MILITARY,
        ]:
            source = models.IncidentSource.RESPONDER
        elif current_user.role == models.UserRole.VERIFIER:
            source = models.IncidentSource.OPS_CENTER
        else:
            source = models.IncidentSource.CITIZEN
    else:
        source = models.IncidentSource.CITIZEN

    # --- AI Triage Engine ---
    # Analyze the text to determine severity and type automatically
    ai_result = ai_engine.analyze(f"{incident.title} {incident.description}")
    
    # Prepare data for DB
    incident_data = incident.model_dump()
    
    # Apply AI Severity (Always trust AI for risk assessment in this MVP)
    incident_data['severity'] = ai_result['severity']
    
    # Apply AI Type if the user selected "Other" or if we want to auto-classify
    # For now, let's prioritize the AI's classification if it found something specific
    if ai_result['incident_type'] != models.IncidentType.OTHER:
        incident_data['incident_type'] = ai_result['incident_type']

    incident_data["source"] = source

    # --- Basic deduping: find recent incidents within ~0.5 km with similar title ---
    def nearby_duplicates():
        candidates = db.query(models.Incident).filter(
            models.Incident.created_at >= datetime.utcnow() - timedelta(hours=2)
        ).all()
        for cand in candidates:
            # Rough distance calc (not accurate for production; placeholder)
            dx = cand.latitude - incident.latitude
            dy = cand.longitude - incident.longitude
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < 0.005 and cand.title.lower() == incident.title.lower():
                return cand
        return None

    potential_dup = nearby_duplicates()
    if potential_dup:
        incident_data["potential_duplicate_id"] = potential_dup.id

    db_incident = models.Incident(
        **incident_data,
        reporter_id=reporter_id,
        status=models.IncidentStatus.PENDING
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    # Broadcast update
    background_tasks.add_task(manager.broadcast, "refresh_incidents")

    # --- Automated Alerting Logic ---
    # If severity is HIGH or CRITICAL, generate a system-wide alert
    if db_incident.severity in [models.IncidentSeverity.HIGH, models.IncidentSeverity.CRITICAL]:
        alert = models.Alert(
            title=f"NEW {db_incident.severity.value.upper()} THREAT",
            message=f"{db_incident.incident_type.value.title()} reported at {db_incident.title}. Immediate attention required.",
            severity=db_incident.severity,
            incident_id=db_incident.id
        )
        db.add(alert)
        db.commit()
        background_tasks.add_task(manager.broadcast, "refresh_alerts")

    return db_incident

@app.get("/incidents/", response_model=List[schemas.IncidentResponse])
def read_incidents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    incidents = db.query(models.Incident).offset(skip).limit(limit).all()
    return incidents

@app.patch("/incidents/{incident_id}", response_model=schemas.IncidentResponse)
def update_incident_status(incident_id: int, status: models.IncidentStatus, background_tasks: BackgroundTasks, unit_id: int = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Check permissions
    if current_user.role not in dispatcher_roles:
        raise HTTPException(status_code=403, detail="Not authorized to update incident status")

    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    allowed_transitions = {
        models.IncidentStatus.PENDING: [
            models.IncidentStatus.VERIFIED,
            models.IncidentStatus.DISPATCHED,
            models.IncidentStatus.RESOLVED,
            models.IncidentStatus.FALSE_ALARM,
        ],
        models.IncidentStatus.VERIFIED: [
            models.IncidentStatus.DISPATCHED,
            models.IncidentStatus.RESOLVED,
            models.IncidentStatus.FALSE_ALARM,
        ],
        models.IncidentStatus.DISPATCHED: [
            models.IncidentStatus.RESOLVED,
            models.IncidentStatus.FALSE_ALARM,
        ],
        models.IncidentStatus.RESOLVED: [],
        models.IncidentStatus.FALSE_ALARM: [],
    }

    if status not in allowed_transitions.get(incident.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {incident.status.value} to {status.value}",
        )
    
    incident.status = status
    
    # Handle Unit Assignment
    if unit_id:
        unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        
        # Assign unit to incident
        incident.assigned_unit_id = unit.id
        
        # Update unit status to BUSY
        unit.status = models.UnitStatus.BUSY
        
        # If status is DISPATCHED, ensure we save that too
        if status == models.IncidentStatus.DISPATCHED:
            pass # Already set above

    now = datetime.utcnow()
    if status == models.IncidentStatus.VERIFIED:
        incident.verified_by_id = current_user.id
        incident.verified_at = now
    if status == models.IncidentStatus.DISPATCHED:
        incident.dispatched_by_id = current_user.id
        incident.dispatched_at = now
    if status in [models.IncidentStatus.RESOLVED, models.IncidentStatus.FALSE_ALARM]:
        incident.resolved_by_id = current_user.id
        incident.resolved_at = now

    # If incident is resolved, free up the unit
    if status == models.IncidentStatus.RESOLVED and incident.assigned_unit_id:
        unit = db.query(models.Unit).filter(models.Unit.id == incident.assigned_unit_id).first()
        if unit:
            unit.status = models.UnitStatus.IDLE
            # We keep the record of who was assigned, but they are now free

    db.commit()
    db.refresh(incident)
    background_tasks.add_task(manager.broadcast, "refresh_incidents")
    background_tasks.add_task(manager.broadcast, "refresh_units")
    return incident

@app.post("/incidents/{incident_id}/flag", response_model=schemas.IncidentResponse)
def flag_incident(incident_id: int, reason: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role not in admin_roles + [models.UserRole.VERIFIER]:
        raise HTTPException(status_code=403, detail="Not authorized to flag incidents")
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.flagged = 1
    incident.flag_reason = reason
    incident.flagged_by_id = current_user.id
    db.commit()
    db.refresh(incident)
    return incident

@app.post("/incidents/{incident_id}/merge", response_model=schemas.IncidentResponse)
def merge_incident(incident_id: int, target_incident_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role not in admin_roles + [models.UserRole.VERIFIER]:
        raise HTTPException(status_code=403, detail="Not authorized to merge incidents")
    if incident_id == target_incident_id:
        raise HTTPException(status_code=400, detail="Cannot merge incident into itself")
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    target = db.query(models.Incident).filter(models.Incident.id == target_incident_id).first()
    if not incident or not target:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.duplicate_of_id = target.id
    incident.status = models.IncidentStatus.FALSE_ALARM
    db.commit()
    db.refresh(incident)
    return incident

@app.get("/alerts/", response_model=List[schemas.AlertResponse])
def read_alerts(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    alerts = db.query(models.Alert).order_by(models.Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts

@app.post("/alerts/", response_model=schemas.AlertResponse)
def create_alert(alert: schemas.AlertCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Only senior command roles can broadcast alerts
    if current_user.role not in admin_roles:
        raise HTTPException(status_code=403, detail="Not authorized to broadcast alerts")
    
    db_alert = models.Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    background_tasks.add_task(manager.broadcast, "refresh_alerts")
    return db_alert

# --- Comment Endpoints ---

@app.post("/incidents/{incident_id}/comments/", response_model=schemas.CommentResponse)
def create_comment(incident_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_comment = models.Comment(
        **comment.model_dump(),
        incident_id=incident_id,
        user_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.post("/incidents/{incident_id}/attachments/", response_model=schemas.AttachmentResponse)
def create_attachment(incident_id: int, attachment: schemas.AttachmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    db_attach = models.IncidentAttachment(
        incident_id=incident_id,
        url=attachment.url,
        media_type=attachment.media_type,
        metadata=attachment.metadata
    )
    db.add(db_attach)
    db.commit()
    db.refresh(db_attach)
    return db_attach

@app.get("/incidents/{incident_id}/comments/", response_model=List[schemas.CommentResponse])
def read_comments(incident_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.incident_id == incident_id).order_by(models.Comment.created_at.desc()).all()
    return comments

# --- Analytics Endpoints ---

@app.get("/analytics/stats")
def get_stats(db: Session = Depends(get_db)):
    total_incidents = db.query(models.Incident).count()
    
    # Count by status
    status_counts = db.query(models.Incident.status, func.count(models.Incident.id)).group_by(models.Incident.status).all()
    status_data = {status: count for status, count in status_counts}
    
    # Count by severity
    severity_counts = db.query(models.Incident.severity, func.count(models.Incident.id)).group_by(models.Incident.severity).all()
    severity_data = {severity: count for severity, count in severity_counts}
    
    return {
        "total_incidents": total_incidents,
        "by_status": status_data,
        "by_severity": severity_data
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.exception("Database health check failed")
        db_status = f"error: {exc}"
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "environment": settings.environment
    }
