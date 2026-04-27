"""
Authentication and authorization utilities.

Handles JWT token generation, validation, and permission checks.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from uuid import UUID
import logging

from config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """JWT token payload."""
    user_id: UUID
    organization_id: UUID
    email: str
    role: str
    exp: datetime


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: UUID,
    organization_id: UUID,
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User ID
        organization_id: Organization ID
        email: User email
        role: User role
        expires_delta: Token expiration time (default: 24 hours)
    
    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiration_hours)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "user_id": str(user_id),
        "organization_id": str(organization_id),
        "email": email,
        "role": role,
        "exp": expire,
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        
        return TokenData(
            user_id=UUID(payload.get("user_id")),
            organization_id=UUID(payload.get("organization_id")),
            email=payload.get("email"),
            role=payload.get("role"),
            exp=datetime.fromtimestamp(payload.get("exp")),
        )
    
    except JWTError as e:
        logger.error(f"Token decode error: {e}")
        return None


def extract_token_from_header(authorization: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Expected format: "Bearer <token>"
    """
    if not authorization:
        return None
    
    parts = authorization.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


class PermissionChecker:
    """Helper for checking permissions."""
    
    @staticmethod
    def can_manage_organization(user_role: str) -> bool:
        """Check if user can manage organization settings."""
        return user_role in ["admin"]
    
    @staticmethod
    def can_manage_users(user_role: str) -> bool:
        """Check if user can manage users."""
        return user_role in ["admin", "leader"]
    
    @staticmethod
    def can_publish_arrangement(user_role: str) -> bool:
        """Check if user can publish arrangements."""
        return user_role in ["admin", "leader"]
    
    @staticmethod
    def can_create_setlist(user_role: str) -> bool:
        """Check if user can create setlists."""
        return user_role in ["admin", "leader", "musician"]
    
    @staticmethod
    def can_view_library(user_role: str) -> bool:
        """Check if user can view library."""
        return user_role in ["admin", "leader", "musician", "viewer"]
    
    @staticmethod
    def can_edit_arrangement(user_role: str, arrangement_published: bool) -> bool:
        """Check if user can edit an arrangement."""
        if not arrangement_published:
            # Anyone can edit draft arrangements
            return True
        
        # Only leaders and admins can edit published arrangements
        return user_role in ["admin", "leader"]
