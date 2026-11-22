from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request payload"""
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class UserResponse(BaseModel):
    """User information returned in auth response"""
    user_id: str
    username: str
    display_name: str
    roles: list[str]
    primary_role: str
    
    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """Login response with token and user info"""
    auth_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field(default="Bearer", description="Token type")
    session_id: str = Field(..., description="Session identifier")
    user: UserResponse = Field(..., description="User information")


class LogoutRequest(BaseModel):
    """Logout request payload"""
    session_id: str = Field(..., description="Session ID to revoke")
