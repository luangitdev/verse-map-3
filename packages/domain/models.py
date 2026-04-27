"""
Core domain models for the Music Analysis Platform.

These models represent the fundamental business entities and rules.
They are independent of any specific framework or persistence layer.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID


class AnalysisPhase(str, Enum):
    """Phases of the analysis pipeline."""
    QUEUED = "queued"
    EXTRACTING_METADATA = "extracting_metadata"
    FETCHING_TEXT = "fetching_text"
    SEPARATING_SOURCES = "separating_sources"
    ANALYZING_AUDIO = "analyzing_audio"
    POSTPROCESSING_STRUCTURE = "postprocessing_structure"
    READY = "ready"
    FAILED = "failed"
    PARTIAL = "partial"


class SectionType(str, Enum):
    """Types of song sections."""
    INTRO = "intro"
    VERSE = "verse"
    PRE_CHORUS = "pre_chorus"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    INTERLUDE = "interlude"
    SPEECH = "speech"
    INSTRUMENTAL = "instrumental"
    OUTRO = "outro"


class UserRole(str, Enum):
    """User roles within an organization."""
    ADMIN = "admin"
    LEADER = "leader"
    MUSICIAN = "musician"
    VIEWER = "viewer"


class SetlistStatus(str, Enum):
    """Status of a setlist."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    EXECUTED = "executed"


@dataclass
class Organization:
    """Organization entity (church, worship group, etc.)."""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class User:
    """User entity within an organization."""
    id: UUID
    organization_id: UUID
    email: str
    name: str
    role: UserRole
    created_at: datetime
    updated_at: datetime


@dataclass
class Song:
    """Song entity (canonical music record)."""
    id: UUID
    organization_id: UUID
    title: str
    artist: Optional[str]
    duration_seconds: int
    created_at: datetime
    updated_at: datetime


@dataclass
class SongSource:
    """Source of a song (YouTube, file, etc.)."""
    id: UUID
    song_id: UUID
    source_type: str  # "youtube", "file", "url"
    source_url: str
    video_id: Optional[str]
    metadata: dict  # YouTube metadata: title, channel, thumbnail, etc.
    created_at: datetime


@dataclass
class SongAnalysis:
    """Analysis result for a song."""
    id: UUID
    song_id: UUID
    phase: AnalysisPhase
    bpm: Optional[float]
    bpm_confidence: float  # 0.0-1.0
    key: Optional[str]  # e.g., "C major", "A minor"
    key_confidence: float  # 0.0-1.0
    time_signature: Optional[str]  # e.g., "4/4"
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class SongSection:
    """Structural section of a song."""
    id: UUID
    analysis_id: UUID
    section_type: SectionType
    start_time: float  # seconds
    end_time: float  # seconds
    label: str  # user-friendly name
    confidence: float  # 0.0-1.0
    order: int
    created_at: datetime


@dataclass
class LyricsLine:
    """Line of lyrics aligned to time."""
    id: UUID
    analysis_id: UUID
    text: str
    start_time: float  # seconds
    end_time: float  # seconds
    is_speech: bool  # True if spoken, False if sung
    created_at: datetime


@dataclass
class ChordChart:
    """Chord chart for a song."""
    id: UUID
    analysis_id: UUID
    key: str  # Original key
    chords: list  # List of {time, chord, confidence}
    created_at: datetime


@dataclass
class Arrangement:
    """Editable arrangement of a song."""
    id: UUID
    song_id: UUID
    organization_id: UUID
    name: str  # e.g., "Original", "Acoustic", "Morning Worship"
    key: str  # Execution key
    sections: list  # List of section edits
    chords: Optional[ChordChart]
    notes: Optional[str]
    published: bool
    published_by: Optional[UUID]  # User ID
    version: int
    created_at: datetime
    updated_at: datetime


@dataclass
class Setlist:
    """Collection of songs for a presentation."""
    id: UUID
    organization_id: UUID
    name: str
    status: SetlistStatus
    created_by: UUID  # User ID
    created_at: datetime
    updated_at: datetime


@dataclass
class SetlistItem:
    """Item in a setlist."""
    id: UUID
    setlist_id: UUID
    arrangement_id: UUID
    order: int
    key: str  # Execution key
    notes: Optional[str]
    duration_seconds: int
    created_at: datetime


@dataclass
class AuditLog:
    """Audit trail for critical changes."""
    id: UUID
    organization_id: UUID
    user_id: UUID
    action: str  # "create", "update", "publish", "delete"
    entity_type: str  # "song", "arrangement", "setlist"
    entity_id: UUID
    changes: dict  # What changed
    created_at: datetime


# Business Rules

class TranspositionRule:
    """Rule for transposing chords between keys."""
    
    NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    @staticmethod
    def transpose_chord(chord: str, from_key: str, to_key: str) -> str:
        """
        Transpose a chord from one key to another.
        
        Args:
            chord: Chord symbol (e.g., "C", "Dm", "G7")
            from_key: Original key (e.g., "C major")
            to_key: Target key (e.g., "D major")
        
        Returns:
            Transposed chord
        
        Raises:
            ValueError: If chord or key is invalid
        """
        # Parse root note from chord
        root = chord[0]
        if len(chord) > 1 and chord[1] == "#":
            root = chord[:2]
        
        if root not in TranspositionRule.NOTES:
            raise ValueError(f"Invalid chord root: {root}")
        
        # Extract key root (e.g., "C" from "C major")
        from_root = from_key.split()[0]
        to_root = to_key.split()[0]
        
        if from_root not in TranspositionRule.NOTES or to_root not in TranspositionRule.NOTES:
            raise ValueError(f"Invalid key: {from_key} or {to_key}")
        
        # Calculate semitone shift
        from_idx = TranspositionRule.NOTES.index(from_root)
        to_idx = TranspositionRule.NOTES.index(to_root)
        shift = (to_idx - from_idx) % 12
        
        # Apply shift to chord root
        root_idx = TranspositionRule.NOTES.index(root)
        new_root_idx = (root_idx + shift) % 12
        new_root = TranspositionRule.NOTES[new_root_idx]
        
        # Preserve chord quality
        quality = chord[len(root):]
        return new_root + quality


class VersioningRule:
    """Rule for arrangement versioning."""
    
    @staticmethod
    def can_edit(arrangement: Arrangement, user: User) -> bool:
        """
        Check if a user can edit an arrangement.
        
        Only leaders can edit published arrangements.
        Anyone can edit draft arrangements in their organization.
        """
        if arrangement.organization_id != user.organization_id:
            return False
        
        if arrangement.published and user.role not in [UserRole.ADMIN, UserRole.LEADER]:
            return False
        
        return True
    
    @staticmethod
    def can_publish(arrangement: Arrangement, user: User) -> bool:
        """Check if a user can publish an arrangement."""
        if arrangement.organization_id != user.organization_id:
            return False
        
        return user.role in [UserRole.ADMIN, UserRole.LEADER]


class SetlistRule:
    """Rule for setlist management."""
    
    @staticmethod
    def can_modify_executed_setlist(setlist: Setlist) -> bool:
        """
        Check if a setlist can be modified.
        
        Executed setlists are immutable to preserve history.
        """
        return setlist.status != SetlistStatus.EXECUTED
    
    @staticmethod
    def mark_as_executed(setlist: Setlist) -> Setlist:
        """Mark a setlist as executed (immutable)."""
        setlist.status = SetlistStatus.EXECUTED
        return setlist


class AnalysisRule:
    """Rule for analysis management."""
    
    @staticmethod
    def is_analysis_complete(analysis: SongAnalysis) -> bool:
        """Check if analysis is complete and ready for use."""
        return analysis.phase in [AnalysisPhase.READY, AnalysisPhase.PARTIAL]
    
    @staticmethod
    def has_low_confidence(analysis: SongAnalysis, threshold: float = 0.6) -> bool:
        """Check if analysis has low confidence scores."""
        return (analysis.bpm_confidence < threshold or 
                analysis.key_confidence < threshold)
