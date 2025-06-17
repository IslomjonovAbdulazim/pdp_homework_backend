from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str
    device_name: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class SessionResponse(BaseModel):
    id: int
    device_name: str
    ip_address: str
    last_login: datetime
    expires_at: datetime
    is_current: bool = False


class DeviceConflictResponse(BaseModel):
    message: str
    active_sessions: list[SessionResponse]