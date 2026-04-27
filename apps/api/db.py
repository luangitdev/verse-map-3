"""
Database utilities and query helpers.

Provides reusable database operations and transaction management.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional
import logging

from models import (
    Organization, User, Song, SongAnalysis, SongSection,
    Arrangement, Setlist, SetlistItem, AuditLog,
    AnalysisPhaseEnum, UserRoleEnum
)

logger = logging.getLogger(__name__)


class SongQueries:
    """Query helpers for songs."""
    
    @staticmethod
    async def get_song_by_id(
        db: AsyncSession,
        song_id: UUID,
        organization_id: UUID,
    ) -> Optional[Song]:
        """Get song by ID with RLS enforcement."""
        result = await db.execute(
            select(Song).where(
                and_(
                    Song.id == song_id,
                    Song.organization_id == organization_id,
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_songs_by_organization(
        db: AsyncSession,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[List[Song], int]:
        """List songs in organization with pagination."""
        query = select(Song).where(Song.organization_id == organization_id)
        
        if search:
            query = query.where(
                or_(
                    Song.title.ilike(f"%{search}%"),
                    Song.artist.ilike(f"%{search}%"),
                )
            )
        
        # Get total count
        count_result = await db.execute(
            select(func.count(Song.id)).where(Song.organization_id == organization_id)
        )
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            query.offset(skip).limit(limit)
        )
        songs = result.scalars().all()
        
        return songs, total
    
    @staticmethod
    async def create_song(
        db: AsyncSession,
        song_id: UUID,
        organization_id: UUID,
        title: str,
        artist: Optional[str] = None,
        duration_seconds: Optional[int] = None,
    ) -> Song:
        """Create a new song."""
        song = Song(
            id=song_id,
            organization_id=organization_id,
            title=title,
            artist=artist,
            duration_seconds=duration_seconds,
        )
        db.add(song)
        await db.flush()
        return song


class AnalysisQueries:
    """Query helpers for analysis."""
    
    @staticmethod
    async def get_analysis_by_id(
        db: AsyncSession,
        analysis_id: UUID,
        organization_id: UUID,
    ) -> Optional[SongAnalysis]:
        """Get analysis by ID with RLS enforcement."""
        result = await db.execute(
            select(SongAnalysis).where(SongAnalysis.id == analysis_id)
            .join(Song)
            .where(Song.organization_id == organization_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_analysis(
        db: AsyncSession,
        analysis_id: UUID,
        song_id: UUID,
    ) -> SongAnalysis:
        """Create a new analysis."""
        analysis = SongAnalysis(
            id=analysis_id,
            song_id=song_id,
            phase=AnalysisPhaseEnum.QUEUED,
        )
        db.add(analysis)
        await db.flush()
        return analysis
    
    @staticmethod
    async def update_analysis_phase(
        db: AsyncSession,
        analysis_id: UUID,
        phase: AnalysisPhaseEnum,
        **kwargs,
    ) -> SongAnalysis:
        """Update analysis phase and optional fields."""
        result = await db.execute(
            select(SongAnalysis).where(SongAnalysis.id == analysis_id)
        )
        analysis = result.scalar_one()
        
        analysis.phase = phase
        for key, value in kwargs.items():
            if hasattr(analysis, key):
                setattr(analysis, key, value)
        
        await db.flush()
        return analysis


class ArrangementQueries:
    """Query helpers for arrangements."""
    
    @staticmethod
    async def get_arrangement_by_id(
        db: AsyncSession,
        arrangement_id: UUID,
        organization_id: UUID,
    ) -> Optional[Arrangement]:
        """Get arrangement by ID with RLS enforcement."""
        result = await db.execute(
            select(Arrangement).where(
                and_(
                    Arrangement.id == arrangement_id,
                    Arrangement.organization_id == organization_id,
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_arrangements_by_song(
        db: AsyncSession,
        song_id: UUID,
        organization_id: UUID,
    ) -> List[Arrangement]:
        """List arrangements for a song."""
        result = await db.execute(
            select(Arrangement).where(
                and_(
                    Arrangement.song_id == song_id,
                    Arrangement.organization_id == organization_id,
                )
            ).order_by(Arrangement.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def create_arrangement(
        db: AsyncSession,
        arrangement_id: UUID,
        song_id: UUID,
        organization_id: UUID,
        name: str,
        key: str,
        **kwargs,
    ) -> Arrangement:
        """Create a new arrangement."""
        arrangement = Arrangement(
            id=arrangement_id,
            song_id=song_id,
            organization_id=organization_id,
            name=name,
            key=key,
            **kwargs,
        )
        db.add(arrangement)
        await db.flush()
        return arrangement
    
    @staticmethod
    async def can_user_edit_arrangement(
        user: User,
        arrangement: Arrangement,
    ) -> bool:
        """Check if user can edit arrangement."""
        # User must be in same organization
        if user.organization_id != arrangement.organization_id:
            return False
        
        # If arrangement is published, only leaders and admins can edit
        if arrangement.published:
            return user.role in [UserRoleEnum.ADMIN, UserRoleEnum.LEADER]
        
        # Draft arrangements can be edited by anyone in org
        return True
    
    @staticmethod
    async def can_user_publish_arrangement(user: User) -> bool:
        """Check if user can publish arrangements."""
        return user.role in [UserRoleEnum.ADMIN, UserRoleEnum.LEADER]


class SetlistQueries:
    """Query helpers for setlists."""
    
    @staticmethod
    async def get_setlist_by_id(
        db: AsyncSession,
        setlist_id: UUID,
        organization_id: UUID,
    ) -> Optional[Setlist]:
        """Get setlist by ID with RLS enforcement."""
        result = await db.execute(
            select(Setlist).where(
                and_(
                    Setlist.id == setlist_id,
                    Setlist.organization_id == organization_id,
                )
            ).options(selectinload(Setlist.items))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_setlists_by_organization(
        db: AsyncSession,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Setlist], int]:
        """List setlists in organization."""
        query = select(Setlist).where(Setlist.organization_id == organization_id)
        
        # Get total count
        count_result = await db.execute(
            select(func.count(Setlist.id)).where(Setlist.organization_id == organization_id)
        )
        total = count_result.scalar()
        
        # Get paginated results
        result = await db.execute(
            query.offset(skip).limit(limit).order_by(Setlist.created_at.desc())
        )
        setlists = result.scalars().all()
        
        return setlists, total
    
    @staticmethod
    async def create_setlist(
        db: AsyncSession,
        setlist_id: UUID,
        organization_id: UUID,
        name: str,
        created_by: UUID,
    ) -> Setlist:
        """Create a new setlist."""
        setlist = Setlist(
            id=setlist_id,
            organization_id=organization_id,
            name=name,
            created_by=created_by,
        )
        db.add(setlist)
        await db.flush()
        return setlist


class AuditQueries:
    """Query helpers for audit logs."""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        organization_id: UUID,
        user_id: UUID,
        action: str,
        entity_type: str,
        entity_id: UUID,
        changes: dict = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        log = AuditLog(
            id=UUID(int=0),  # Will be auto-generated
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes or {},
        )
        db.add(log)
        await db.flush()
        return log


class TransactionManager:
    """Manages database transactions."""
    
    @staticmethod
    async def begin_transaction(db: AsyncSession):
        """Begin a transaction."""
        await db.begin()
    
    @staticmethod
    async def commit_transaction(db: AsyncSession):
        """Commit a transaction."""
        await db.commit()
    
    @staticmethod
    async def rollback_transaction(db: AsyncSession):
        """Rollback a transaction."""
        await db.rollback()
