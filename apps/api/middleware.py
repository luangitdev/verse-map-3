"""
Middleware for the Music Analysis Platform API.
"""

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


async def set_organization_context(request: Request, call_next):
    """
    Middleware to set organization context for RLS.
    
    Extracts organization_id from JWT token and sets it in the database session.
    """
    # TODO: Extract organization_id from JWT token
    # For now, we'll use a placeholder
    
    organization_id = request.headers.get("X-Organization-ID")
    
    if organization_id:
        try:
            # Validate UUID format
            UUID(organization_id)
            request.state.organization_id = organization_id
        except ValueError:
            logger.warning(f"Invalid organization ID format: {organization_id}")
    
    response = await call_next(request)
    return response


async def set_rls_context(session: AsyncSession, organization_id: str):
    """
    Set RLS context in the database session.
    
    This function sets the app.current_organization_id variable in PostgreSQL,
    which is used by RLS policies to filter data.
    """
    try:
        await session.execute(
            text(f"SELECT app.set_organization_context('{organization_id}'::uuid)")
        )
    except Exception as e:
        logger.error(f"Failed to set RLS context: {e}")
        raise
