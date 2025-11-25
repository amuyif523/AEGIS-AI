from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

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
    
    # Classification
    incident_type = Column(Enum(IncidentType), default=IncidentType.OTHER)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.LOW)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.PENDING)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign Keys
    reporter_id = Column(Integer, ForeignKey("users.id"))
    assigned_unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    
    # Relationships
    reporter = relationship("User", back_populates="reports")
    assigned_unit = relationship("Unit")

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
