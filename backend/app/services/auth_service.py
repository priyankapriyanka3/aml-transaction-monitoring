import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..config import settings
from ..models.session_record import SessionRecord
from ..models.user import User
from ..repositories.session_repository import SessionRepository
from ..repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication and session management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
    
    def login(self, username: str, password: str) -> tuple[str, str, User] | None:
        """
        Authenticate user and create session.
        Returns (auth_token, session_id, user) or None if invalid credentials.
        """
        # Get user by username
        user = self.user_repo.get_by_username(username)
        if not user or not user.is_active:
            return None
        
        # Verify password using bcrypt
        if not self._verify_password(password, user.password_hash):
            return None
        
        # Generate session ID
        session_id_uuid = uuid.uuid4()
        session_id = str(session_id_uuid)
        
        # Create JWT token
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes)
        token_data = {
            "sub": str(user.user_id),
            "username": user.username,
            "session_id": session_id,
            "exp": expires_at
        }
        auth_token = jwt.encode(token_data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        
        # Hash token for storage
        token_hash = hashlib.sha256(auth_token.encode()).hexdigest()
        
        # Create session record
        session = SessionRecord(
            session_id=session_id_uuid,
            user_id=user.user_id,
            token_hash=token_hash,
            issued_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            last_activity_at=datetime.now(timezone.utc)
        )
        self.session_repo.create(session)
        
        return auth_token, session_id, user
    
    def logout(self, session_id: str) -> bool:
        """
        Revoke session by session ID.
        Returns True if successful, False if session not found.
        """
        session = self.session_repo.get_by_session_id(session_id)
        if not session:
            return False
        
        self.session_repo.revoke(session)
        return True
    
    def validate_token(self, token: str) -> User | None:
        """
        Validate JWT token and return user if valid.
        Checks token signature, expiry, and session status.
        """
        try:
            # Decode JWT
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            user_id: str = payload.get("sub")
            session_id: str = payload.get("session_id")
            
            if not user_id or not session_id:
                return None
            
            # Hash token to check against session record
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Check session is valid (not revoked, not expired)
            session = self.session_repo.get_by_token_hash(token_hash)
            if not session:
                return None
            
            # SQLite stores datetimes as naive UTC; compare as naive
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
            expires_naive = session.expires_at.replace(tzinfo=None) if session.expires_at.tzinfo else session.expires_at
            if expires_naive < now_utc:
                return None
            
            # Get user (convert string UUID from JWT to uuid.UUID)
            user = self.user_repo.get_by_id(uuid.UUID(user_id))
            if not user or not user.is_active:
                return None
            
            return user
            
        except JWTError:
            return None
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt"""
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with cost factor >= 12"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
