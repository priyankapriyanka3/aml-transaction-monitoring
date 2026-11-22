from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.auth_schemas import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    UserResponse,
)
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and create session.
    Returns JWT token, session ID, and user information.
    """
    auth_service = AuthService(db)
    result = auth_service.login(request.username, request.password)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    auth_token, session_id, user = result
    
    # Build user response
    user_response = UserResponse(
        user_id=str(user.user_id),
        username=user.username,
        display_name=user.display_name,
        roles=[user.primary_role],
        primary_role=user.primary_role
    )
    
    return LoginResponse(
        auth_token=auth_token,
        session_id=session_id,
        user=user_response
    )


@router.post("/logout")
def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    """
    Revoke session by session ID.
    """
    auth_service = AuthService(db)
    success = auth_service.logout(request.session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"detail": "Session revoked successfully", "session_id": request.session_id}
