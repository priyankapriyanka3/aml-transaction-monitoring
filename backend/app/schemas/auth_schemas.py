"""Authentication request and response schemas."""
import uuid
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request with email and password."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class UserResponse(BaseModel):
    """User information in authentication response."""
    
    user_id: uuid.UUID = Field(..., description="User UUID")
    display_name: str = Field(..., description="User display name")
    email: str = Field(..., description="User email address")
    role: str = Field(..., description="User role")
    
    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """Successful login response with JWT token."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")
    user: UserResponse = Field(..., description="Authenticated user information")


class LogoutResponse(BaseModel):
    """Logout response."""
    
    detail: str = Field(default="Logged out successfully")


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    detail: str = Field(..., description="Error message")
