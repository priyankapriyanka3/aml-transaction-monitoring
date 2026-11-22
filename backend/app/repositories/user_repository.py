from sqlalchemy.orm import Session

from ..models.user import User


class UserRepository:
    """Repository for user data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_username(self, username: str) -> User | None:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID"""
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def get_by_email(self, email: str) -> User | None:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
