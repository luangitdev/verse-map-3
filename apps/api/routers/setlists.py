"""
Setlists router - creation, management, and live mode.

Handles setlist CRUD operations, item management, and live presentation mode.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import uuid4, UUID
from datetime import datetime
import logging

from models import (
    Setlist, SetlistItem, Arrangement, Song, SetlistStatusEnum,
    User, UserRoleEnum, AuditLog
)
from packages.contracts import (
    CreateSetlistRequest, AddSetlistItemRequest,
    SetlistResponse, SetlistDetailResponse
)
from middleware import set_rls_context
from db import SetlistQueries, ArrangementQueries, AuditQueries
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
    "/setlists",
    response_model=SetlistResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_setlist(
    request: CreateSetlistRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Create a new setlist.
    
    Initial status is DRAFT. Can be edited until EXECUTED.
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        # Create setlist
        setlist_id = uuid4()
        setlist = Setlist(
            id=setlist_id,
            organization_id=current_user.organization_id,
            name=request.name,
            created_by=UUID(current_user.user_id),
        )
        db.add(setlist)
        
        # Log action
        await AuditQueries.log_action(
            db,
            current_user.organization_id,
            UUID(current_user.user_id),
            "create",
            "setlist",
            setlist_id,
            {"name": setlist.name},
        )
        
        await db.commit()
        
        logger.info(f"Created setlist {setlist_id}")
        
        return SetlistResponse(
            id=setlist.id,
            name=setlist.name,
            status=setlist.status.value,
            created_by=setlist.created_by,
            created_at=setlist.created_at,
        )
    
    except Exception as e:
        logger.error(f"Error creating setlist: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create setlist",
        )


@router.get(
    "/setlists/{setlist_id}",
    response_model=SetlistDetailResponse,
)
async def get_setlist(
    setlist_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Retrieve setlist with all items.
    
    Includes arrangement details for each item.
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        setlist = await SetlistQueries.get_setlist_by_id(
            db,
            setlist_id,
            current_user.organization_id,
        )
        
        if not setlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setlist not found",
            )
        
        # Build items response
        items = []
        for item in setlist.items:
            items.append({
                "id": item.id,
                "arrangement_id": item.arrangement_id,
                "order": item.order,
                "key": item.key,
                "notes": item.notes,
                "duration_seconds": item.duration_seconds,
                "created_at": item.created_at,
            })
        
        return SetlistDetailResponse(
            id=setlist.id,
            name=setlist.name,
            status=setlist.status.value,
            items=items,
            created_by=setlist.created_by,
            created_at=setlist.created_at,
            updated_at=setlist.updated_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting setlist: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get setlist",
        )


@router.post(
    "/setlists/{setlist_id}/items",
    status_code=status.HTTP_201_CREATED,
)
async def add_setlist_item(
    setlist_id: UUID,
    request: AddSetlistItemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Add an arrangement to a setlist.
    
    The arrangement must be published. The execution key specifies the key
    the song will be performed in (may differ from original).
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        # Get setlist
        setlist = await SetlistQueries.get_setlist_by_id(
            db,
            setlist_id,
            current_user.organization_id,
        )
        
        if not setlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setlist not found",
            )
        
        # Check if setlist can be modified
        if setlist.status == SetlistStatusEnum.EXECUTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify executed setlist",
            )
        
        # Get arrangement
        arrangement = await ArrangementQueries.get_arrangement_by_id(
            db,
            request.arrangement_id,
            current_user.organization_id,
        )
        
        if not arrangement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arrangement not found",
            )
        
        if not arrangement.published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only published arrangements can be added to setlists",
            )
        
        # Get max order
        max_order_result = await db.execute(
            select(SetlistItem).where(SetlistItem.setlist_id == setlist_id)
        )
        items = max_order_result.scalars().all()
        next_order = max([item.order for item in items], default=0) + 1
        
        # Create setlist item
        item_id = uuid4()
        item = SetlistItem(
            id=item_id,
            setlist_id=setlist_id,
            arrangement_id=request.arrangement_id,
            order=next_order,
            key=request.key,
            notes=request.notes,
            duration_seconds=request.duration_seconds,
        )
        db.add(item)
        
        # Log action
        await AuditQueries.log_action(
            db,
            current_user.organization_id,
            UUID(current_user.user_id),
            "add_item",
            "setlist",
            setlist_id,
            {"arrangement_id": str(request.arrangement_id), "order": next_order},
        )
        
        await db.commit()
        
        logger.info(f"Added arrangement {request.arrangement_id} to setlist {setlist_id}")
        
        return {
            "id": item.id,
            "arrangement_id": item.arrangement_id,
            "order": item.order,
            "key": item.key,
            "created_at": item.created_at,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding setlist item: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to setlist",
        )


@router.patch("/setlist-items/{item_id}")
async def update_setlist_item(
    item_id: UUID,
    request: dict,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Update a setlist item.
    
    Allows reordering, changing key, and editing notes.
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        # Get item
        result = await db.execute(
            select(SetlistItem).where(SetlistItem.id == item_id)
            .join(Setlist)
            .where(Setlist.organization_id == current_user.organization_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setlist item not found",
            )
        
        # Check if setlist can be modified
        setlist_result = await db.execute(
            select(Setlist).where(Setlist.id == item.setlist_id)
        )
        setlist = setlist_result.scalar_one()
        
        if setlist.status == SetlistStatusEnum.EXECUTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify executed setlist",
            )
        
        # Update fields
        if "order" in request:
            item.order = request["order"]
        if "key" in request:
            item.key = request["key"]
        if "notes" in request:
            item.notes = request["notes"]
        
        # Log action
        await AuditQueries.log_action(
            db,
            current_user.organization_id,
            UUID(current_user.user_id),
            "update_item",
            "setlist",
            item.setlist_id,
            {"item_id": str(item_id), "changes": request},
        )
        
        await db.commit()
        
        logger.info(f"Updated setlist item {item_id}")
        
        return {
            "id": item.id,
            "order": item.order,
            "key": item.key,
            "notes": item.notes,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating setlist item: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update setlist item",
        )


@router.post("/setlists/{setlist_id}/live/start")
async def start_live_mode(
    setlist_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Start live mode for a setlist.
    
    Transitions setlist to EXECUTED status and returns live session info.
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        # Get setlist
        setlist = await SetlistQueries.get_setlist_by_id(
            db,
            setlist_id,
            current_user.organization_id,
        )
        
        if not setlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setlist not found",
            )
        
        if setlist.status == SetlistStatusEnum.EXECUTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Setlist is already executed",
            )
        
        # Mark as executed
        setlist.status = SetlistStatusEnum.EXECUTED
        setlist.updated_at = datetime.utcnow()
        
        # Log action
        await AuditQueries.log_action(
            db,
            current_user.organization_id,
            UUID(current_user.user_id),
            "start_live",
            "setlist",
            setlist_id,
            {"status": "executed"},
        )
        
        await db.commit()
        
        logger.info(f"Started live mode for setlist {setlist_id}")
        
        # Build live session response
        items = []
        for item in setlist.items:
            items.append({
                "id": item.id,
                "arrangement_id": item.arrangement_id,
                "order": item.order,
                "key": item.key,
            })
        
        return {
            "setlist_id": setlist.id,
            "status": "live",
            "items": items,
            "current_item_index": 0,
            "started_at": datetime.utcnow().isoformat(),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting live mode: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start live mode",
        )


@router.get("/setlists/{setlist_id}/live/status")
async def get_live_status(
    setlist_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Get live mode status for a setlist.
    
    Returns current song, section, and navigation info.
    """
    
    try:
        await set_rls_context(db, str(current_user.organization_id))
        
        setlist = await SetlistQueries.get_setlist_by_id(
            db,
            setlist_id,
            current_user.organization_id,
        )
        
        if not setlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setlist not found",
            )
        
        if setlist.status != SetlistStatusEnum.EXECUTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Setlist is not in live mode",
            )
        
        # Build items list
        items = []
        for item in setlist.items:
            items.append({
                "id": item.id,
                "arrangement_id": item.arrangement_id,
                "order": item.order,
                "key": item.key,
                "duration_seconds": item.duration_seconds,
            })
        
        return {
            "setlist_id": setlist.id,
            "status": "live",
            "items": items,
            "total_items": len(items),
            "updated_at": setlist.updated_at.isoformat(),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting live status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get live status",
        )


@router.get("/organizations/{organization_id}/setlists")
async def list_setlists(
    organization_id: UUID,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    List setlists in organization.
    
    Filtered by organization and paginated.
    """
    
    try:
        # Verify user is in organization
        if current_user.organization_id != str(organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other organization's setlists",
            )
        
        await set_rls_context(db, str(organization_id))
        
        setlists, total = await SetlistQueries.list_setlists_by_organization(
            db,
            organization_id,
            skip,
            limit,
        )
        
        return {
            "items": [
                {
                    "id": s.id,
                    "name": s.name,
                    "status": s.status.value,
                    "created_by": s.created_by,
                    "created_at": s.created_at,
                }
                for s in setlists
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing setlists: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list setlists",
        )
