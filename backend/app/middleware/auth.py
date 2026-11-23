"""Authentication middleware and dependency injection."""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get the current authenticated user.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Authenticated User object
        
    Raises:
        HTTPException: If authentication fails (401)
    """
    token = credentials.credentials
    
    auth_service = AuthService(db)
    user = auth_service.verify_session(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to get current active user.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Active User object
        
    Raises:
        HTTPException: If user is not active (403)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


def require_role(*allowed_roles: str):
    """Dependency factory to require specific user roles.
    
    Args:
        allowed_roles: One or more allowed role names
        
    Returns:
        Dependency function that checks user role
    """
    def check_role(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return check_role
