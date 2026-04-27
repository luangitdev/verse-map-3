"""
Test fixtures and factories for creating test data.
"""

from datetime import datetime
from uuid import uuid4
from packages.domain.models import (
    Organization, User, Song, SongSource, SongAnalysis, SongSection,
    LyricsLine, ChordChart, Arrangement, Setlist, SetlistItem, AuditLog,
    AnalysisPhase, SectionType, UserRole, SetlistStatus
)


class OrganizationFactory:
    """Factory for creating Organization test data."""
    
    @staticmethod
    def create(
        id=None,
        name="Test Church",
        description="A test organization",
        created_at=None,
        updated_at=None
    ):
        return Organization(
            id=id or uuid4(),
            name=name,
            description=description,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )


class UserFactory:
    """Factory for creating User test data."""
    
    @staticmethod
    def create(
        id=None,
        organization_id=None,
        email="user@test.com",
        name="Test User",
        role=UserRole.MUSICIAN,
        created_at=None,
        updated_at=None
    ):
        return User(
            id=id or uuid4(),
            organization_id=organization_id or uuid4(),
            email=email,
            name=name,
            role=role,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )


class SongFactory:
    """Factory for creating Song test data."""
    
    @staticmethod
    def create(
        id=None,
        organization_id=None,
        title="Test Song",
        artist="Test Artist",
        duration_seconds=180,
        created_at=None,
        updated_at=None
    ):
        return Song(
            id=id or uuid4(),
            organization_id=organization_id or uuid4(),
            title=title,
            artist=artist,
            duration_seconds=duration_seconds,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )


class SongSourceFactory:
    """Factory for creating SongSource test data."""
    
    @staticmethod
    def create(
        id=None,
        song_id=None,
        source_type="youtube",
        source_url="https://youtube.com/watch?v=test",
        video_id="test_video_id",
        metadata=None,
        created_at=None
    ):
        return SongSource(
            id=id or uuid4(),
            song_id=song_id or uuid4(),
            source_type=source_type,
            source_url=source_url,
            video_id=video_id,
            metadata=metadata or {"title": "Test", "channel": "Test Channel"},
            created_at=created_at or datetime.now()
        )


class SongAnalysisFactory:
    """Factory for creating SongAnalysis test data."""
    
    @staticmethod
    def create(
        id=None,
        song_id=None,
        phase=AnalysisPhase.READY,
        bpm=120.0,
        bpm_confidence=0.85,
        key="C major",
        key_confidence=0.80,
        time_signature="4/4",
        error_message=None,
        created_at=None,
        updated_at=None
    ):
        return SongAnalysis(
            id=id or uuid4(),
            song_id=song_id or uuid4(),
            phase=phase,
            bpm=bpm,
            bpm_confidence=bpm_confidence,
            key=key,
            key_confidence=key_confidence,
            time_signature=time_signature,
            error_message=error_message,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )


class SongSectionFactory:
    """Factory for creating SongSection test data."""
    
    @staticmethod
    def create(
        id=None,
        analysis_id=None,
        section_type=SectionType.VERSE,
        start_time=0.0,
        end_time=30.0,
        label="Verse 1",
        confidence=0.85,
        order=1,
        created_at=None
    ):
        return SongSection(
            id=id or uuid4(),
            analysis_id=analysis_id or uuid4(),
            section_type=section_type,
            start_time=start_time,
            end_time=end_time,
            label=label,
            confidence=confidence,
            order=order,
            created_at=created_at or datetime.now()
        )


class LyricsLineFactory:
    """Factory for creating LyricsLine test data."""
    
    @staticmethod
    def create(
        id=None,
        analysis_id=None,
        text="Test lyrics",
        start_time=0.0,
        end_time=5.0,
        is_speech=False,
        created_at=None
    ):
        return LyricsLine(
            id=id or uuid4(),
            analysis_id=analysis_id or uuid4(),
            text=text,
            start_time=start_time,
            end_time=end_time,
            is_speech=is_speech,
            created_at=created_at or datetime.now()
        )


class ChordChartFactory:
    """Factory for creating ChordChart test data."""
    
    @staticmethod
    def create(
        id=None,
        analysis_id=None,
        key="C major",
        chords=None,
        created_at=None
    ):
        if chords is None:
            chords = [
                {"time": 0.0, "chord": "C", "confidence": 0.9},
                {"time": 5.0, "chord": "F", "confidence": 0.85},
                {"time": 10.0, "chord": "G", "confidence": 0.88},
            ]
        
        return ChordChart(
            id=id or uuid4(),
            analysis_id=analysis_id or uuid4(),
            key=key,
            chords=chords,
            created_at=created_at or datetime.now()
        )


class ArrangementFactory:
    """Factory for creating Arrangement test data."""
    
    @staticmethod
    def create(
        id=None,
        song_id=None,
        organization_id=None,
        name="Original",
        key="C major",
        sections=None,
        chords=None,
        notes=None,
        published=False,
        published_by=None,
        version=1,
        created_at=None,
        updated_at=None
    ):
        return Arrangement(
            id=id or uuid4(),
            song_id=song_id or uuid4(),
            organization_id=organization_id or uuid4(),
            name=name,
            key=key,
            sections=sections or [],
            chords=chords,
            notes=notes,
            published=published,
            published_by=published_by,
            version=version,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )


class SetlistFactory:
    """Factory for creating Setlist test data."""
    
    @staticmethod
    def create(
        id=None,
        organization_id=None,
        name="Sunday Service",
        status=SetlistStatus.DRAFT,
        created_by=None,
        created_at=None,
        updated_at=None
    ):
        return Setlist(
            id=id or uuid4(),
            organization_id=organization_id or uuid4(),
            name=name,
            status=status,
            created_by=created_by or uuid4(),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )


class SetlistItemFactory:
    """Factory for creating SetlistItem test data."""
    
    @staticmethod
    def create(
        id=None,
        setlist_id=None,
        arrangement_id=None,
        order=1,
        key="C major",
        notes=None,
        duration_seconds=180,
        created_at=None
    ):
        return SetlistItem(
            id=id or uuid4(),
            setlist_id=setlist_id or uuid4(),
            arrangement_id=arrangement_id or uuid4(),
            order=order,
            key=key,
            notes=notes,
            duration_seconds=duration_seconds,
            created_at=created_at or datetime.now()
        )


class AuditLogFactory:
    """Factory for creating AuditLog test data."""
    
    @staticmethod
    def create(
        id=None,
        organization_id=None,
        user_id=None,
        action="create",
        entity_type="song",
        entity_id=None,
        changes=None,
        created_at=None
    ):
        return AuditLog(
            id=id or uuid4(),
            organization_id=organization_id or uuid4(),
            user_id=user_id or uuid4(),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id or uuid4(),
            changes=changes or {},
            created_at=created_at or datetime.now()
        )
