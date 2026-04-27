"""
Authentication router - login, token refresh, and user info.

Handles JWT-based authentication and user session management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from models import User, Organization, UserRoleEnum
from middleware import set_rls_context
from auth import (
    create_access_token, decode_access_token, verify_password,
    hash_password, extract_token_from_header, TokenData
)
from db import AuditQueries

logger = logging.getLogger(__name__)
router = APIRouter()


class LoginRequest(BaseModel):
    """Login request."""
    email: str
    password: str
    organization_id: str


class LoginResponse(BaseModel):
    """Login response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    organization_id: str
    email: str
    name: str
    role: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class UserInfoResponse(BaseModel):
    """User info response."""
    id: str
    email: str
    name: str
    role: str
    organization_id: str


async def get_db() -> AsyncSession:
    """Get database session."""
    pass


async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> TokenData:
    """
    Get current authenticated user from JWT token.
    
    Validates token and returns user data.
    """
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    
    token = extract_token_from_header(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    token_data = decode_access_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    return token_data


@router.post("/auth/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT token.
    
    TODO: In production, integrate with OAuth provider or secure password storage.
    For now, this is a placeholder for the authentication flow.
    """
    
    try:
        await set_rls_context(db, request.organization_id)
        
        # Get organization
        org_result = await db.execute(
            select(Organization).where(Organization.id == UUID(request.organization_id))
        )
        organization = org_result.scalar_one_or_none()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        
        # Get user
        user_result = await db.execute(
            select(User).where(
                and_(
                    User.email == request.email,
                    User.organization_id == UUID(request.organization_id),
                )
            )
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        # TODO: Verify password hash
        # if not verify_password(request.password, user.password_hash):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Invalid email or password",
        #     )
        
        # Create access token
        access_token = create_access_token(
            user_id=user.id,
            organization_id=user.organization_id,
            email=user.email,
            role=user.role.value,
        )
        
        # Log action
        await AuditQueries.log_action(
            db,
            user.organization_id,
            user.id,
            "login",
            "user",
            user.id,
            {"email": user.email},
        )
        
        await db.commit()
        
        logger.info(f"User {user.email} logged in")
        
        return LoginResponse(
            access_token=access_token,
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            email=user.email,
            name=user.name,
            role=user.role.value,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/auth/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
):
    """
    Refresh access token using refresh token.
    
    TODO: Implement refresh token logic with separate token type.
    """
    
    # Decode refresh token
    token_data = decode_access_token(request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    # Create new access token
    access_token = create_access_token(
        user_id=UUID(token_data.user_id),
        organization_id=UUID(token_data.organization_id),
        email=token_data.email,
        role=token_data.role,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/auth/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
):
    """
    Get current user information.
    
    Returns authenticated user's profile.
    """
    
    return UserInfoResponse(
        id=current_user.user_id,
        email=current_user.email,
        name="User",  # TODO: Get from database
        role=current_user.role,
        organization_id=current_user.organization_id,
    )


@router.post("/auth/logout")
async def logout(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user.
    
    Logs the logout action in audit trail.
    In JWT-based auth, logout is client-side (token invalidation).
    """
    
    try:
        await set_rls_context(db, current_user.organization_id)
        
        # Log action
        await AuditQueries.log_action(
            db,
            UUID(current_user.organization_id),
            UUID(current_user.user_id),
            "logout",
            "user",
            UUID(current_user.user_id),
            {"email": current_user.email},
        )
        
        await db.commit()
        
        logger.info(f"User {current_user.email} logged out")
        
        return {"message": "Logged out successfully"}
    
    except Exception as e:
        logger.error(f"Logout error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )
