"""
Songs router - import, retrieval, and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import uuid4, UUID
from datetime import datetime
import logging

from models import Song, SongSource, SongAnalysis, AnalysisPhaseEnum
from packages.contracts import (
    ImportYoutubeRequest, ImportYoutubeResponse, SongResponse,
    SongDetailResponse, ErrorResponse
)
from middleware import set_rls_context
from celery_tasks import analyze_song_task

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db() -> AsyncSession:
    """Get database session."""
    # This will be injected by FastAPI dependency injection
    pass


@router.post(
    "/songs/import-youtube",
    response_model=ImportYoutubeResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def import_youtube(
    request: ImportYoutubeRequest,
    db: AsyncSession = Depends(get_db),
    organization_id: str = Depends(lambda: None),  # From middleware
):
    """
    Import a song from YouTube URL.
    
    Returns immediately with analysis_id and queued status.
    Dispatches async job to analysis pipeline.
    """
    
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID is required",
        )
    
    try:
        # Set RLS context
        await set_rls_context(db, organization_id)
        
        # Extract video ID from URL (simplified)
        video_id = str(request.url).split("v=")[-1].split("&")[0]
        
        if not video_id or len(video_id) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid YouTube URL",
            )
        
        # Create song record
        song_id = uuid4()
        song = Song(
            id=song_id,
            organization_id=UUID(organization_id),
            title=request.title or f"Song {video_id}",
            duration_seconds=0,  # Will be updated by worker
        )
        db.add(song)
        
        # Create song source
        source = SongSource(
            id=uuid4(),
            song_id=song_id,
            source_type="youtube",
            source_url=str(request.url),
            video_id=video_id,
            metadata={"imported_at": datetime.utcnow().isoformat()},
        )
        db.add(source)
        
        # Create analysis record
        analysis_id = uuid4()
        analysis = SongAnalysis(
            id=analysis_id,
            song_id=song_id,
            phase=AnalysisPhaseEnum.QUEUED,
        )
        db.add(analysis)
        
        await db.commit()
        
        # Dispatch async job
        task = analyze_song_task.delay(
            song_id=str(song_id),
            analysis_id=str(analysis_id),
            video_id=video_id,
            organization_id=organization_id,
        )
        
        logger.info(f"Dispatched analysis job {task.id} for song {song_id}")
        
        return ImportYoutubeResponse(
            analysis_id=analysis_id,
            song_id=song_id,
            status="queued",
            message="Analysis queued successfully",
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing YouTube URL: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to import song",
        )


@router.get("/analyses/{analysis_id}", response_model=dict)
async def get_analysis_status(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    organization_id: str = Depends(lambda: None),
):
    """
    Poll analysis status and progress.
    
    Returns current phase, BPM, key, and confidence scores.
    """
    
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID is required",
        )
    
    try:
        await set_rls_context(db, organization_id)
        
        # Query analysis
        result = await db.execute(
            select(SongAnalysis).where(SongAnalysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found",
            )
        
        return {
            "id": analysis.id,
            "song_id": analysis.song_id,
            "phase": analysis.phase.value,
            "bpm": analysis.bpm,
            "bpm_confidence": analysis.bpm_confidence,
            "key": analysis.key,
            "key_confidence": analysis.key_confidence,
            "error_message": analysis.error_message,
            "created_at": analysis.created_at.isoformat(),
            "updated_at": analysis.updated_at.isoformat(),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analysis status",
        )


@router.get("/songs/{song_id}", response_model=SongDetailResponse)
async def get_song(
    song_id: UUID,
    db: AsyncSession = Depends(get_db),
    organization_id: str = Depends(lambda: None),
):
    """
    Retrieve song with metadata and analysis results.
    """
    
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID is required",
        )
    
    try:
        await set_rls_context(db, organization_id)
        
        # Query song
        result = await db.execute(
            select(Song).where(Song.id == song_id)
        )
        song = result.scalar_one_or_none()
        
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found",
            )
        
        # TODO: Build full response with analysis, sections, lyrics, chords
        
        return {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "duration_seconds": song.duration_seconds,
            "created_at": song.created_at.isoformat(),
            "updated_at": song.updated_at.isoformat(),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting song: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get song",
        )


@router.get("/organizations/{organization_id}/library")
async def list_songs(
    organization_id: UUID,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    List songs in organization library.
    """
    
    try:
        await set_rls_context(db, str(organization_id))
        
        # Query songs
        result = await db.execute(
            select(Song)
            .where(Song.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
        )
        songs = result.scalars().all()
        
        # Get total count
        count_result = await db.execute(
            select(Song).where(Song.organization_id == organization_id)
        )
        total = len(count_result.scalars().all())
        
        return {
            "items": [
                {
                    "id": song.id,
                    "title": song.title,
                    "artist": song.artist,
                    "duration_seconds": song.duration_seconds,
                    "created_at": song.created_at.isoformat(),
                }
                for song in songs
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    
    except Exception as e:
        logger.error(f"Error listing songs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list songs",
        )
