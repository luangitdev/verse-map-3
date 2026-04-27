"""
Arrangements router - editing, versioning, and publishing.

Handles arrangement CRUD operations, section editing, chord management, and publishing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import uuid4, UUID
from datetime import datetime
import logging

from models import (
    Arrangement, Song, SongAnalysis, SongSection, ChordChart,
    User, UserRoleEnum, AuditLog
)
from packages.contracts import (
    CreateArrangementRequest, UpdateSectionsRequest, UpdateChordsRequest,
    ArrangementResponse, ArrangementDetailResponse
)
from middleware import set_rls_context
from db import ArrangementQueries, AuditQueries
from auth import PermissionChecker, TokenData

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db() -> AsyncSession:
    """Get database session."""
    pass


async def get_current_user(token: str = None) -> TokenData:
    """Get current authenticated user."""
    # TODO: Extract from JWT token
    pass


@router.post(
    "/songs/{song_id}/arrangements",
    response_model=ArrangementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_arrangement(
    song_id: UUID,
    request: CreateArrangementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Create a new arrangement for a song.
    
    The arrangement is initially a copy of the analysis results.
    It can be edited independently without affecting the raw analysis.
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        # Verify song exists and belongs to organization
        result = await db.execute(
            select(Song).where(
                and_(
                    Song.id == song_id,
                    Song.organization_id == current_user.organization_id,
                )
            )
        )
        song = result.scalar_one_or_none()
        
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found",
            )
        
        # Get latest analysis
        analysis_result = await db.execute(
            select(SongAnalysis)
            .where(SongAnalysis.song_id == song_id)
            .order_by(SongAnalysis.created_at.desc())
        )
        analysis = analysis_result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No analysis available for this song",
            )
        
        # Create arrangement
        arrangement_id = uuid4()
        arrangement = Arrangement(
            id=arrangement_id,
            song_id=song_id,
            organization_id=current_user.organization_id,
            name=request.name or f"{song.title} - Arrangement",
            key=request.key or analysis.key or "Unknown",
            sections=request.sections or [],
            chords=request.chords,
            notes=request.notes,
        )
        db.add(arrangement)
        
        # Log action
        await AuditQueries.log_action(
            db,
            current_user.organization_id,
            UUID(current_user.user_id),
            "create",
            "arrangement",
            arrangement_id,
            {"song_id": str(song_id), "name": arrangement.name},
        )
        
        await db.commit()
        
        logger.info(f"Created arrangement {arrangement_id} for song {song_id}")
        
        return ArrangementResponse(
            id=arrangement.id,
            song_id=arrangement.song_id,
            name=arrangement.name,
            key=arrangement.key,
            published=arrangement.published,
            version=arrangement.version,
            created_at=arrangement.created_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating arrangement: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create arrangement",
        )


@router.get(
    "/arrangements/{arrangement_id}",
    response_model=ArrangementDetailResponse,
)
async def get_arrangement(
    arrangement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Retrieve arrangement with all details.
    
    Includes sections, chords, and metadata.
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        arrangement = await ArrangementQueries.get_arrangement_by_id(
            db,
            arrangement_id,
            current_user.organization_id,
        )
        
        if not arrangement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arrangement not found",
            )
        
        return ArrangementDetailResponse(
            id=arrangement.id,
            song_id=arrangement.song_id,
            name=arrangement.name,
            key=arrangement.key,
            sections=arrangement.sections,
            chords=arrangement.chords,
            notes=arrangement.notes,
            published=arrangement.published,
            published_by=arrangement.published_by,
            version=arrangement.version,
            created_at=arrangement.created_at,
            updated_at=arrangement.updated_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting arrangement: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get arrangement",
        )


@router.patch(
    "/arrangements/{arrangement_id}/sections",
    response_model=ArrangementResponse,
)
async def update_sections(
    arrangement_id: UUID,
    request: UpdateSectionsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Update arrangement sections.
    
    Allows renaming, reordering, and marking sections as speech.
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        # Get arrangement
        arrangement = await ArrangementQueries.get_arrangement_by_id(
            db,
            arrangement_id,
            current_user.organization_id,
        )
        
        if not arrangement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arrangement not found",
            )
        
        # Check permissions
        can_edit = await ArrangementQueries.can_user_edit_arrangement(
            User(
                id=UUID(current_user.user_id),
                organization_id=current_user.organization_id,
                role=UserRoleEnum(current_user.role),
            ),
            arrangement,
        )
        
        if not can_edit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot edit published arrangement",
            )
        
        # Update sections
        old_sections = arrangement.sections
        arrangement.sections = request.sections
        arrangement.version += 1
        
        # Log action
        await AuditQueries.log_action(
            db,
            current_user.organization_id,
            UUID(current_user.user_id),
            "update",
            "arrangement",
            arrangement_id,
            {"sections_updated": True, "version": arrangement.version},
        )
        
        await db.commit()
        
        logger.info(f"Updated sections for arrangement {arrangement_id}")
        
        return ArrangementResponse(
            id=arrangement.id,
            song_id=arrangement.song_id,
            name=arrangement.name,
            key=arrangement.key,
            published=arrangement.published,
            version=arrangement.version,
            created_at=arrangement.created_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sections: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update sections",
        )


@router.patch(
    "/arrangements/{arrangement_id}/chords",
    response_model=ArrangementResponse,
)
async def update_chords(
    arrangement_id: UUID,
    request: UpdateChordsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Update arrangement chords.
    
    Allows editing individual chords and transposing to new keys.
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        # Get arrangement
        arrangement = await ArrangementQueries.get_arrangement_by_id(
            db,
            arrangement_id,
            current_user.organization_id,
        )
        
        if not arrangement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arrangement not found",
            )
        
        # Check permissions
        can_edit = await ArrangementQueries.can_user_edit_arrangement(
            User(
                id=UUID(current_user.user_id),
                organization_id=current_user.organization_id,
                role=UserRoleEnum(current_user.role),
            ),
            arrangement,
        )
        
        if not can_edit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot edit published arrangement",
            )
        
        # Update chords
        arrangement.chords = request.chords
        if request.new_key:
            arrangement.key = request.new_key
        arrangement.version += 1
        
        # Log action
        await AuditQueries.log_action(
            db,
            current_user.organization_id,
            UUID(current_user.user_id),
            "update",
            "arrangement",
            arrangement_id,
            {"chords_updated": True, "new_key": request.new_key, "version": arrangement.version},
        )
        
        await db.commit()
        
        logger.info(f"Updated chords for arrangement {arrangement_id}")
        
        return ArrangementResponse(
            id=arrangement.id,
            song_id=arrangement.song_id,
            name=arrangement.name,
            key=arrangement.key,
            published=arrangement.published,
            version=arrangement.version,
            created_at=arrangement.created_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chords: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chords",
        )


@router.post(
    "/arrangements/{arrangement_id}/publish",
    response_model=ArrangementResponse,
)
async def publish_arrangement(
    arrangement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Publish an arrangement.
    
    Only leaders and admins can publish arrangements.
    Published arrangements cannot be edited (only leaders can override).
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        # Check permissions
        if not PermissionChecker.can_publish_arrangement(current_user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only leaders and admins can publish arrangements",
            )
        
        # Get arrangement
        arrangement = await ArrangementQueries.get_arrangement_by_id(
            db,
            arrangement_id,
            current_user.organization_id,
        )
        
        if not arrangement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arrangement not found",
            )
        
        if arrangement.published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arrangement is already published",
            )
        
        # Publish arrangement
        arrangement.published = True
        arrangement.published_by = UUID(current_user.user_id)
        
        # Log action
        await AuditQueries.log_action(
            db,
            current_user.organization_id,
            UUID(current_user.user_id),
            "publish",
            "arrangement",
            arrangement_id,
            {"published_by": str(current_user.user_id)},
        )
        
        await db.commit()
        
        logger.info(f"Published arrangement {arrangement_id}")
        
        return ArrangementResponse(
            id=arrangement.id,
            song_id=arrangement.song_id,
            name=arrangement.name,
            key=arrangement.key,
            published=arrangement.published,
            version=arrangement.version,
            created_at=arrangement.created_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing arrangement: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish arrangement",
        )


@router.get("/songs/{song_id}/arrangements")
async def list_arrangements(
    song_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    List all arrangements for a song.
    
    Returns arrangements in reverse chronological order (newest first).
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        # Verify song exists
        result = await db.execute(
            select(Song).where(
                and_(
                    Song.id == song_id,
                    Song.organization_id == current_user.organization_id,
                )
            )
        )
        song = result.scalar_one_or_none()
        
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found",
            )
        
        # List arrangements
        arrangements = await ArrangementQueries.list_arrangements_by_song(
            db,
            song_id,
            current_user.organization_id,
        )
        
        return {
            "items": [
                {
                    "id": arr.id,
                    "name": arr.name,
                    "key": arr.key,
                    "published": arr.published,
                    "version": arr.version,
                    "created_at": arr.created_at,
                }
                for arr in arrangements
            ],
            "total": len(arrangements),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing arrangements: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list arrangements",
        )
