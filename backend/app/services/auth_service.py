"""Authentication service for login, logout, and session management."""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.models.session import Session as SessionModel
from app.core.security import (
    verify_password,
    create_access_token,
    hash_token,
    decode_access_token
)
from app.config import settings


class AuthService:
    """Authentication and session management service."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        stmt = select(User).where(User.email == email, User.is_active == True)
        user = self.db.scalars(stmt).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def create_session(
        self,
        user: User,
        correlation_id: Optional[str] = None
    ) -> tuple[str, SessionModel]:
        """Create a new session for an authenticated user.
        
        Args:
            user: Authenticated user
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            Tuple of (JWT token, Session record)
        """
        # Create JWT token
        token, expires_at = create_access_token(
            user.user_id,
            user.role,
            correlation_id
        )
        
        # Hash token for storage
        token_hash = hash_token(token)
        
        # Create session record
        now = datetime.now(timezone.utc)
        session = SessionModel(
            user_id=user.user_id,
            hashed_token=token_hash,
            issued_at_utc=now,
            expires_at_utc=expires_at,
            last_activity_utc=now
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return token, session
    
    def login(
        self,
        email: str,
        password: str,
        correlation_id: Optional[str] = None
    ) -> tuple[str, int, User]:
        """Authenticate user and create session.
        
        Args:
            email: User email
            password: User password
            correlation_id: Optional correlation ID
            
        Returns:
            Tuple of (JWT token, expiry seconds, User)
            
        Raises:
            HTTPException: If authentication fails
        """
        user = self.authenticate_user(email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        token, session = self.create_session(user, correlation_id)
        
        # Calculate expiry in seconds
        expires_in = settings.jwt_expiry_minutes * 60
        
        return token, expires_in, user
    
    def logout(self, token: str) -> None:
        """Revoke a session by token.
        
        Args:
            token: JWT token to revoke
        """
        token_hash = hash_token(token)
        
        stmt = select(SessionModel).where(SessionModel.hashed_token == token_hash)
        session = self.db.scalars(stmt).first()
        
        if session:
            self.db.delete(session)
            self.db.commit()
    
    def verify_session(self, token: str) -> Optional[User]:
        """Verify a JWT token and check session is still active.
        
        Args:
            token: JWT token to verify
            
        Returns:
            User if session is valid, None otherwise
        """
        try:
            # Decode token
            payload = decode_access_token(token)
            user_id = uuid.UUID(payload["sub"])
            
            # Check session exists and is not expired
            token_hash = hash_token(token)
            stmt = select(SessionModel).where(
                SessionModel.hashed_token == token_hash,
                SessionModel.expires_at_utc > datetime.now(timezone.utc)
            )
            session = self.db.scalars(stmt).first()
            
            if not session:
                return None
            
            # Update last activity
            session.last_activity_utc = datetime.now(timezone.utc)
            self.db.commit()
            
            # Get user
            user = self.db.get(User, user_id)
            
            if not user or not user.is_active:
                return None
            
            return user
            
        except Exception:
            return None
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions.
        
        Returns:
            Number of sessions deleted
        """
        now = datetime.now(timezone.utc)
        stmt = select(SessionModel).where(SessionModel.expires_at_utc < now)
        expired = self.db.scalars(stmt).all()
        
        count = len(expired)
        for session in expired:
            self.db.delete(session)
        
        self.db.commit()
        return count
