from pydantic import BaseModel
from datetime import datetime


class SessionResponse(BaseModel):
    id: int
    device_name: str
    ip_address: str
    last_login: datetime
    expires_at: datetime

    class Config:
        from_attributes = True