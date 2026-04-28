"""
SQLAlchemy ORM models for the Music Analysis Platform.

These models map to the PostgreSQL database with Row Level Security.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Enum,
    ForeignKey, JSON, Text, TIMESTAMP, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
import enum

Base = declarative_base()


class AnalysisPhaseEnum(str, enum.Enum):
    """Analysis pipeline phases."""
    QUEUED = "queued"
    EXTRACTING_METADATA = "extracting_metadata"
    FETCHING_TEXT = "fetching_text"
    SEPARATING_SOURCES = "separating_sources"
    ANALYZING_AUDIO = "analyzing_audio"
    POSTPROCESSING_STRUCTURE = "postprocessing_structure"
    READY = "ready"
    FAILED = "failed"
    PARTIAL = "partial"


class SectionTypeEnum(str, enum.Enum):
    """Section types."""
    INTRO = "intro"
    VERSE = "verse"
    PRE_CHORUS = "pre_chorus"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    INTERLUDE = "interlude"
    SPEECH = "speech"
    INSTRUMENTAL = "instrumental"
    OUTRO = "outro"


class UserRoleEnum(str, enum.Enum):
    """User roles."""
    ADMIN = "admin"
    LEADER = "leader"
    MUSICIAN = "musician"
    VIEWER = "viewer"


class SetlistStatusEnum(str, enum.Enum):
    """Setlist statuses."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    EXECUTED = "executed"


class Organization(Base):
    """Organization entity."""
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    teams = relationship("Team", back_populates="organization")
    songs = relationship("Song", back_populates="organization")
    arrangements = relationship("Arrangement", back_populates="organization")
    setlists = relationship("Setlist", back_populates="organization")
    audit_logs = relationship("AuditLog", back_populates="organization")


class User(Base):
    """User entity."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.MUSICIAN, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    team_memberships = relationship("TeamMember", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_organization", "organization_id"),
        Index("idx_user_email", "email"),
    )


class Team(Base):
    """Team entity (worship team, ministry, etc.)."""
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="teams")
    members = relationship("TeamMember", back_populates="team")


class TeamMember(Base):
    """Team membership."""
    __tablename__ = "team_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")


class Song(Base):
    """Song entity."""
    __tablename__ = "songs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    title = Column(String(255), nullable=False)
    artist = Column(String(255))
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="songs")
    sources = relationship("SongSource", back_populates="song")
    analyses = relationship("SongAnalysis", back_populates="song")
    arrangements = relationship("Arrangement", back_populates="song")
    
    # Indexes
    __table_args__ = (
        Index("idx_song_organization", "organization_id"),
    )


class SongSource(Base):
    """Source of a song (YouTube, file, etc.)."""
    __tablename__ = "song_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id"), nullable=False)
    source_type = Column(String(50), nullable=False)  # "youtube", "file", "url"
    source_url = Column(String(2048), nullable=False)
    video_id = Column(String(255))
    source_metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    song = relationship("Song", back_populates="sources")


class SongAnalysis(Base):
    """Analysis result for a song."""
    __tablename__ = "song_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id"), nullable=False)
    phase = Column(Enum(AnalysisPhaseEnum), default=AnalysisPhaseEnum.QUEUED, nullable=False)
    bpm = Column(Float)
    bpm_confidence = Column(Float, default=0.0)
    key = Column(String(50))
    key_confidence = Column(Float, default=0.0)
    time_signature = Column(String(20))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    song = relationship("Song", back_populates="analyses")
    sections = relationship("SongSection", back_populates="analysis")
    lyrics_lines = relationship("LyricsLine", back_populates="analysis")
    chord_charts = relationship("ChordChart", back_populates="analysis")
    
    # Indexes
    __table_args__ = (
        Index("idx_analysis_song", "song_id"),
        Index("idx_analysis_phase", "phase"),
    )


class SongSection(Base):
    """Structural section of a song."""
    __tablename__ = "song_sections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("song_analyses.id"), nullable=False)
    section_type = Column(Enum(SectionTypeEnum), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    label = Column(String(255), nullable=False)
    confidence = Column(Float, default=0.0)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis = relationship("SongAnalysis", back_populates="sections")


class LyricsLine(Base):
    """Line of lyrics aligned to time."""
    __tablename__ = "lyrics_lines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("song_analyses.id"), nullable=False)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    is_speech = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis = relationship("SongAnalysis", back_populates="lyrics_lines")


class ChordChart(Base):
    """Chord chart for a song."""
    __tablename__ = "chord_charts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("song_analyses.id"), nullable=False)
    key = Column(String(50), nullable=False)
    chords = Column(JSONB, default=[])  # List of {time, chord, confidence}
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis = relationship("SongAnalysis", back_populates="chord_charts")


class Arrangement(Base):
    """Editable arrangement of a song."""
    __tablename__ = "arrangements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    key = Column(String(50), nullable=False)
    sections = Column(JSONB, default=[])
    chords = Column(JSONB)
    notes = Column(Text)
    published = Column(Boolean, default=False)
    published_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    song = relationship("Song", back_populates="arrangements")
    organization = relationship("Organization", back_populates="arrangements")
    setlist_items = relationship("SetlistItem", back_populates="arrangement")
    
    # Indexes
    __table_args__ = (
        Index("idx_arrangement_song", "song_id"),
        Index("idx_arrangement_organization", "organization_id"),
    )


class Setlist(Base):
    """Collection of songs for a presentation."""
    __tablename__ = "setlists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Enum(SetlistStatusEnum), default=SetlistStatusEnum.DRAFT, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="setlists")
    items = relationship("SetlistItem", back_populates="setlist")
    
    # Indexes
    __table_args__ = (
        Index("idx_setlist_organization", "organization_id"),
    )


class SetlistItem(Base):
    """Item in a setlist."""
    __tablename__ = "setlist_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setlist_id = Column(UUID(as_uuid=True), ForeignKey("setlists.id"), nullable=False)
    arrangement_id = Column(UUID(as_uuid=True), ForeignKey("arrangements.id"), nullable=False)
    order = Column(Integer, nullable=False)
    key = Column(String(50), nullable=False)
    notes = Column(Text)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    setlist = relationship("Setlist", back_populates="items")
    arrangement = relationship("Arrangement", back_populates="setlist_items")


class AuditLog(Base):
    """Audit trail for critical changes."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # "create", "update", "publish", "delete"
    entity_type = Column(String(50), nullable=False)  # "song", "arrangement", "setlist"
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    changes = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index("idx_audit_organization", "organization_id"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_entity", "entity_type", "entity_id"),
    )
