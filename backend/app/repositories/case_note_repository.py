"""
Repository for case note data operations.
Handles note creation and retrieval.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.case_note import CaseNote
from ..models.user import User


class CaseNoteRepository:
    """Repository for case note operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, note: CaseNote) -> CaseNote:
        """Create a new case note"""
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note
    
    def list_by_case(self, case_id: UUID | str) -> list[CaseNote]:
        """
        List all notes for a case in chronological order (created_at ASC).
        Returns notes from oldest to newest for timeline display.
        """
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        stmt = (
            select(CaseNote)
            .filter(CaseNote.case_id == case_uuid)
            .order_by(CaseNote.created_at.asc())
        )
        return list(self.db.execute(stmt).scalars().all())
    
    def get_user_by_id(self, user_id: UUID | str) -> User | None:
        """Get user by ID for author enrichment"""
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        return self.db.query(User).filter(User.user_id == user_uuid).first()
