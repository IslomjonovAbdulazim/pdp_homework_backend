from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
from ..utils.constants import MAX_FILES_PER_HOMEWORK, MAX_LINES_PER_FILE


class SubmissionFileCreate(BaseModel):
    file_name: str
    content: str

    @validator('content')
    def validate_content(cls, v):
        lines = v.split('\n')
        if len(lines) > MAX_LINES_PER_FILE:
            raise ValueError(f'File cannot exceed {MAX_LINES_PER_FILE} lines')
        return v


class SubmissionCreate(BaseModel):
    files: List[SubmissionFileCreate]

    @validator('files')
    def validate_files(cls, v):
        if len(v) == 0:
            raise ValueError('At least one file is required')
        if len(v) > MAX_FILES_PER_HOMEWORK:
            raise ValueError(f'Cannot submit more than {MAX_FILES_PER_HOMEWORK} files')
        return v


class SubmissionFileResponse(BaseModel):
    id: int
    file_name: str
    content: str
    line_count: int

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    id: int
    homework_id: int
    student_id: int
    submitted_at: datetime
    ai_grade: int
    final_grade: int
    ai_feedback: str
    homework_title: Optional[str] = None
    student_name: Optional[str] = None
    files: List[SubmissionFileResponse] = []

    class Config:
        from_attributes = True