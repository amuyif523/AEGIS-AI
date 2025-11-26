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

    class Config:
        from_attributes = True

# --- Alert Schemas ---
class AlertBase(BaseModel):
    title: str
    message: str
    severity: IncidentSeverity

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
