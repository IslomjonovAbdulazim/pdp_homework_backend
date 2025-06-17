from pydantic import BaseModel
from typing import List
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str
    device_name: str


class SessionResponse(BaseModel):
    id: int
    device_name: str
    ip_address: str
    last_login: datetime
    expires_at: datetime
    is_current: bool = False


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict  # User data as dict to avoid circular imports


class DeviceConflictResponse(BaseModel):
    message: str
    active_sessions: List[SessionResponse]