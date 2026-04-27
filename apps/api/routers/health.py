"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis
import logging

from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends()):
    """Detailed health check with database and Redis status."""
    
    database_status = "unknown"
    redis_status = "unknown"
    
    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        database_status = "ok" if result.scalar() == 1 else "error"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_status = "error"
    
    # Check Redis
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        redis_status = "ok"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "error"
    
    overall_status = "ok" if database_status == "ok" and redis_status == "ok" else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": database_status,
            "redis": redis_status,
        },
    }
