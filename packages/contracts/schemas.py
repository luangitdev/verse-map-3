"""
API contract schemas using Pydantic.

These schemas define the contracts between frontend and backend.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID


# ============================================================================
# Request Schemas
# ============================================================================

class ImportYoutubeRequest(BaseModel):
    """Request to import a song from YouTube."""
    url: HttpUrl = Field(..., description="YouTube URL")
    title: Optional[str] = Field(None, description="Override song title")


class CreateArrangementRequest(BaseModel):
    """Request to create a new arrangement."""
    name: str = Field(..., description="Arrangement name (e.g., 'Original', 'Acoustic')")
    key: str = Field(..., description="Execution key (e.g., 'C major')")
    notes: Optional[str] = Field(None, description="Arrangement notes")


class UpdateSectionsRequest(BaseModel):
    """Request to update arrangement sections."""
    sections: list = Field(..., description="List of section edits")


class UpdateChordsRequest(BaseModel):
    """Request to update chord chart."""
    key: str = Field(..., description="Chord key")
    chords: list = Field(..., description="List of chords with timestamps")


class CreateSetlistRequest(BaseModel):
    """Request to create a setlist."""
    name: str = Field(..., description="Setlist name")


class AddSetlistItemRequest(BaseModel):
    """Request to add a song to a setlist."""
    arrangement_id: UUID = Field(..., description="Arrangement ID")
    key: str = Field(..., description="Execution key")
    notes: Optional[str] = Field(None, description="Item notes")


# ============================================================================
# Response Schemas
# ============================================================================

class SongAnalysisResponse(BaseModel):
    """Response for song analysis status."""
    id: UUID
    song_id: UUID
    phase: str
    bpm: Optional[float] = None
    bpm_confidence: float
    key: Optional[str] = None
    key_confidence: float
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SongSectionResponse(BaseModel):
    """Response for a song section."""
    id: UUID
    section_type: str
    start_time: float
    end_time: float
    label: str
    confidence: float
    order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LyricsLineResponse(BaseModel):
    """Response for a lyrics line."""
    id: UUID
    text: str
    start_time: float
    end_time: float
    is_speech: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChordChartResponse(BaseModel):
    """Response for a chord chart."""
    id: UUID
    key: str
    chords: list
    created_at: datetime
    
    class Config:
        from_attributes = True


class SongResponse(BaseModel):
    """Response for a song."""
    id: UUID
    title: str
    artist: Optional[str] = None
    duration_seconds: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SongDetailResponse(SongResponse):
    """Detailed response for a song with analysis."""
    analysis: Optional[SongAnalysisResponse] = None
    sections: list[SongSectionResponse] = []
    lyrics: list[LyricsLineResponse] = []
    chords: Optional[ChordChartResponse] = None


class ArrangementResponse(BaseModel):
    """Response for an arrangement."""
    id: UUID
    song_id: UUID
    name: str
    key: str
    published: bool
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ArrangementDetailResponse(ArrangementResponse):
    """Detailed response for an arrangement."""
    sections: list = []
    chords: Optional[ChordChartResponse] = None
    notes: Optional[str] = None


class SetlistItemResponse(BaseModel):
    """Response for a setlist item."""
    id: UUID
    arrangement_id: UUID
    order: int
    key: str
    notes: Optional[str] = None
    duration_seconds: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SetlistResponse(BaseModel):
    """Response for a setlist."""
    id: UUID
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SetlistDetailResponse(SetlistResponse):
    """Detailed response for a setlist."""
    items: list[SetlistItemResponse] = []


class ImportYoutubeResponse(BaseModel):
    """Response for YouTube import."""
    analysis_id: UUID = Field(..., description="Analysis ID for polling")
    song_id: UUID = Field(..., description="Song ID")
    status: str = Field(..., description="Current analysis phase")
    message: str = Field(..., description="Status message")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error detail")
    code: Optional[str] = Field(None, description="Error code")


# ============================================================================
# Pagination & Filtering
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of records to return")


class SongFilterParams(PaginationParams):
    """Filter parameters for songs."""
    search: Optional[str] = Field(None, description="Search by title or artist")
    organization_id: Optional[UUID] = Field(None, description="Filter by organization")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: list
    total: int
    skip: int
    limit: int


# ============================================================================
# Status & Health
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str
    redis: str
    timestamp: datetime


class QueueStatusResponse(BaseModel):
    """Queue status response."""
    total_jobs: int
    queued: int
    processing: int
    completed: int
    failed: int
    average_duration_seconds: float
