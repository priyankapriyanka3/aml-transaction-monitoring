"""Authentication routes for login and logout."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth_schemas import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    UserResponse
)
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user, security
from app.models.user import User


router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user with email and password, returns JWT token"
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """Authenticate user and create session.
    
    Args:
        request: Login credentials
        db: Database session
        
    Returns:
        JWT token and user information
    """
    auth_service = AuthService(db)
    token, expires_in, user = auth_service.login(request.email, request.password)
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse(
            user_id=user.user_id,
            display_name=user.display_name,
            email=user.email,
            role=user.role
        )
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Revoke current session token"
)
def logout(
    current_user: User = Depends(get_current_user),
    credentials = Depends(security),
    db: Session = Depends(get_db)
) -> LogoutResponse:
    """Logout user and revoke session.
    
    Args:
        current_user: Current authenticated user
        credentials: Bearer token credentials
        db: Database session
        
    Returns:
        Logout confirmation
    """
    token = credentials.credentials
    auth_service = AuthService(db)
    auth_service.logout(token)
    
    return LogoutResponse(detail="Logged out successfully")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information"
)
def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse(
        user_id=current_user.user_id,
        display_name=current_user.display_name,
        email=current_user.email,
        role=current_user.role
    )
