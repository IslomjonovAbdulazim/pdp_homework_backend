from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class GroupBase(BaseModel):
    name: str


class GroupCreate(GroupBase):
    teacher_id: int


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    teacher_id: Optional[int] = None


class GroupResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    created_at: datetime
    teacher_name: Optional[str] = None
    student_count: int = 0

    class Config:
        from_attributes = True