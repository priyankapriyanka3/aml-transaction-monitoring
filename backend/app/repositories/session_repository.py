import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.session_record import SessionRecord


class SessionRepository:
    """Repository for session record data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, session: SessionRecord) -> SessionRecord:
        """Create a new session record"""
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_by_token_hash(self, token_hash: str) -> SessionRecord | None:
        """Get session by token hash"""
        return self.db.query(SessionRecord).filter(
            SessionRecord.token_hash == token_hash,
            SessionRecord.revoked_at.is_(None)
        ).first()
    
    def get_by_session_id(self, session_id: str | uuid.UUID) -> SessionRecord | None:
        """Get session by session ID"""
        # Convert string to UUID if needed
        if isinstance(session_id, str):
            try:
                session_id = uuid.UUID(session_id)
            except ValueError:
                # Invalid UUID string - return None
                return None
        return self.db.query(SessionRecord).filter(
            SessionRecord.session_id == session_id
        ).first()
    
    def revoke(self, session: SessionRecord) -> SessionRecord:
        """Revoke a session by setting revoked_at timestamp"""
        session.revoked_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(session)
        return session
