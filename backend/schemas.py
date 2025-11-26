from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import IncidentType, IncidentSeverity, IncidentStatus, UserRole, UnitStatus, IncidentSource

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserCreateAdmin(UserCreate):
    role: UserRole

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

# --- Unit Schemas ---
class UnitBase(BaseModel):
    callsign: str
    unit_type: UserRole
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UnitCreate(UnitBase):
    pass

class UnitUpdate(BaseModel):
    status: Optional[UnitStatus] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UnitResponse(UnitBase):
    id: int
    status: UnitStatus
    last_updated: datetime

    class Config:
        from_attributes = True

# --- Incident Schemas ---
class IncidentBase(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float
    incident_type: IncidentType
    severity: Optional[IncidentSeverity] = IncidentSeverity.LOW
    source: Optional[IncidentSource] = IncidentSource.CITIZEN
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    flag_reason: Optional[str] = None
    ai_confidence: Optional[float] = 0.0
    escalation_probability: Optional[float] = 0.0
    spread_risk: Optional[float] = 0.0
    casualty_likelihood: Optional[float] = 0.0
    crowd_size_estimate: Optional[int] = 0
    spatial_risk_index: Optional[float] = 0.0

class IncidentCreate(IncidentBase):
    pass

class IncidentResponse(IncidentBase):
    id: int
    status: IncidentStatus
    created_at: datetime
    reporter_id: int
    assigned_unit_id: Optional[int] = None
    verified_at: Optional[datetime] = None
    dispatched_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    verified_by_id: Optional[int] = None
    dispatched_by_id: Optional[int] = None
    resolved_by_id: Optional[int] = None
    flagged: int
    flagged_by_id: Optional[int] = None
    duplicate_of_id: Optional[int] = None
    potential_duplicate_id: Optional[int] = None
    suggested_agencies: Optional[list[str]] = None
    suggested_unit_type: Optional[str] = None
    routing_rationale: Optional[str] = None
    mission_id: Optional[int] = None

    class Config:
        from_attributes = True

# --- Attachment Schemas ---
class AttachmentBase(BaseModel):
    url: str
    media_type: Optional[str] = None
    metadata: Optional[str] = None

class AttachmentCreate(AttachmentBase):
    pass

class AttachmentResponse(AttachmentBase):
    id: int
    incident_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Mission Schemas ---
class MissionBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class MissionCreate(MissionBase):
    incident_ids: Optional[list[int]] = []

class MissionResponse(MissionBase):
    id: int
    created_at: datetime
    created_by_id: Optional[int] = None

    class Config:
        from_attributes = True

# --- Annotation Schemas ---
class AnnotationBase(BaseModel):
    annotation_type: str
    label: Optional[str] = None
    latitude: float
    longitude: float
    radius_m: Optional[float] = None
    mission_id: Optional[int] = None

class AnnotationCreate(AnnotationBase):
    pass

class AnnotationResponse(AnnotationBase):
    id: int
    created_at: datetime
    created_by_id: Optional[int] = None

    class Config:
        from_attributes = True

# --- Alert Schemas ---
class AlertBase(BaseModel):
    title: str
    message: str
    severity: IncidentSeverity
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = None
    recommended_action: Optional[str] = None
    audience: Optional[str] = None

class AlertCreate(AlertBase):
    incident_id: int

class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    incident_id: int

    class Config:
        from_attributes = True

# --- Comment Schemas ---
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    user_id: int
    username: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
