from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base, SQLALCHEMY_DATABASE_URL
from geoalchemy2 import Geometry

IS_POSTGRES = "postgresql" in SQLALCHEMY_DATABASE_URL

# --- Enums for Standardization ---
class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    POLICE = "police"
    MEDICAL = "medical"
    FIRE = "fire"
    TRAFFIC = "traffic"
    DISASTER = "disaster_coordinator"
    MILITARY = "military_analyst"
    NATIONAL_SUPERVISOR = "national_supervisor"
    VERIFIER = "verifier"
    SYS_ADMIN = "sys_admin"
    ADMIN = "admin"  # legacy/backwards-compatible
    COMMAND = "command"  # legacy/backwards-compatible

class IncidentType(str, enum.Enum):
    CRIME = "crime"
    MEDICAL = "medical"
    FIRE = "fire"
    ACCIDENT = "accident"
    HAZARD = "hazard"
    UNREST = "unrest"
    FLOOD = "flood"
    INFRASTRUCTURE = "infrastructure"
    CROWD = "crowd"
    SUSPICIOUS = "suspicious"
    OTHER = "other"

class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentSource(str, enum.Enum):
    CITIZEN = "citizen"
    RESPONDER = "responder"
    OPS_CENTER = "ops_center"
    SENSOR = "sensor"
    WEATHER = "weather"
    OTHER = "other"

class IncidentStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    DISPATCHED = "dispatched"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"

class UnitStatus(str, enum.Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"

# --- Database Models ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    reports = relationship("Incident", back_populates="reporter")

class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    callsign = Column(String, unique=True, index=True)  # e.g., "ALPHA-1"
    unit_type = Column(Enum(UserRole)) # Reusing UserRole (POLICE, FIRE, MEDICAL)
    status = Column(Enum(UnitStatus), default=UnitStatus.IDLE)
    
    # Current Location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    
    # Geospatial Data (Storing as floats for simplicity in MVP, PostGIS Geometry later)
    latitude = Column(Float)
    longitude = Column(Float)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326)) if IS_POSTGRES else Column(String, nullable=True)
    
    # Classification
    incident_type = Column(Enum(IncidentType), default=IncidentType.OTHER)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.LOW)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.PENDING)
    source = Column(Enum(IncidentSource), default=IncidentSource.CITIZEN)
    media_url = Column(String, nullable=True)
    media_type = Column(String, nullable=True)
    flagged = Column(Integer, default=0)  # 0/1 boolean-ish for SQLite portability
    flag_reason = Column(String, nullable=True)
    duplicate_of_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    potential_duplicate_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    escalation_probability = Column(Float, nullable=True)
    spread_risk = Column(Float, nullable=True)
    casualty_likelihood = Column(Float, nullable=True)
    crowd_size_estimate = Column(Integer, nullable=True)
    
    # Foreign Keys
    reporter_id = Column(Integer, ForeignKey("users.id"))
    assigned_unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    dispatched_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    flagged_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    suggested_agencies = Column(String, nullable=True)  # store as comma-separated for simplicity
    suggested_unit_type = Column(String, nullable=True)
    routing_rationale = Column(String, nullable=True)
    
    # Relationships
    reporter = relationship("User", back_populates="reports")
    assigned_unit = relationship("Unit")
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    dispatched_by = relationship("User", foreign_keys=[dispatched_by_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    flagged_by = relationship("User", foreign_keys=[flagged_by_id])
    duplicate_of = relationship("Incident", remote_side=[id], foreign_keys=[duplicate_of_id], uselist=False)
    potential_duplicate = relationship("Incident", remote_side=[id], foreign_keys=[potential_duplicate_id], uselist=False)


class IncidentAttachment(Base):
    __tablename__ = "incident_attachments"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    url = Column(String, nullable=False)
    media_type = Column(String, nullable=True)
    metadata = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", backref="attachments")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(String)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.LOW)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Link to the incident that triggered it
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    incident = relationship("Incident")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    incident = relationship("Incident", back_populates="comments")
    author = relationship("User")

    @property
    def username(self):
        return self.author.username if self.author else "Unknown"

# Update Incident relationship
Incident.comments = relationship("Comment", back_populates="incident", order_by="desc(Comment.created_at)")
