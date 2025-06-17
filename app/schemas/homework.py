from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from ..utils.constants import LINE_LIMIT_OPTIONS, FILE_EXTENSION_OPTIONS


class HomeworkBase(BaseModel):
    title: str
    description: str
    points: int
    start_date: datetime
    deadline: datetime
    line_limit: int
    file_extension: str
    ai_grading_prompt: str


class HomeworkCreate(HomeworkBase):
    group_id: int

    @validator('line_limit')
    def validate_line_limit(cls, v):
        if v not in LINE_LIMIT_OPTIONS:
            raise ValueError(f'Line limit must be one of {LINE_LIMIT_OPTIONS}')
        return v

    @validator('file_extension')
    def validate_file_extension(cls, v):
        if v not in FILE_EXTENSION_OPTIONS:
            raise ValueError(f'File extension must be one of {FILE_EXTENSION_OPTIONS}')
        return v


class HomeworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    points: Optional[int] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    line_limit: Optional[int] = None
    file_extension: Optional[str] = None
    ai_grading_prompt: Optional[str] = None


class HomeworkResponse(BaseModel):
    id: int
    title: str
    description: str
    points: int
    start_date: datetime
    deadline: datetime
    line_limit: int
    file_extension: str
    teacher_id: int
    group_id: int
    created_at: datetime
    teacher_name: Optional[str] = None
    group_name: Optional[str] = None
    submission_count: int = 0

    class Config:
        from_attributes = True