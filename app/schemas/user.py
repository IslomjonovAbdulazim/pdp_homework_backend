from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    fullname: str
    username: str
    role: str


class UserCreate(BaseModel):
    fullname: str
    username: str
    password: str
    role: str
    group_id: Optional[int] = None


class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    password: Optional[str] = None
    group_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    fullname: str
    username: str
    role: str
    group_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True