"""Security utilities for password hashing and JWT token management."""
import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
import bcrypt
import jwt
from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with cost factor 12.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hash to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(
    user_id: uuid.UUID,
    role: str,
    correlation_id: Optional[str] = None
) -> tuple[str, datetime]:
    """Create a JWT access token.
    
    Args:
        user_id: User UUID
        role: User role (INVESTIGATOR, OFFICER, etc.)
        correlation_id: Optional correlation ID for request tracking
        
    Returns:
        Tuple of (token string, expiration datetime)
    """
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.jwt_expiry_minutes)
    
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": expires_at,
        "correlation_id": correlation_id or str(uuid.uuid4())
    }
    
    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return token, expires_at


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    return payload


def hash_token(token: str) -> str:
    """Hash a JWT token for storage using SHA-256.
    
    Args:
        token: JWT token string
        
    Returns:
        Hex-encoded hash of the token
    """
    return hashlib.sha256(token.encode('utf-8')).hexdigest()
