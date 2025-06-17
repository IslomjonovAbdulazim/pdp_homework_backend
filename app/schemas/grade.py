from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class GradeUpdate(BaseModel):
    final_task_completeness: Optional[int] = None
    final_code_quality: Optional[int] = None
    final_correctness: Optional[int] = None

    @validator('final_task_completeness', 'final_code_quality', 'final_correctness')
    def validate_scores(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Scores must be between 0 and 100')
        return v


class GradeResponse(BaseModel):
    id: int
    submission_id: int
    ai_task_completeness: int
    ai_code_quality: int
    ai_correctness: int
    ai_total: int
    final_task_completeness: int
    final_code_quality: int
    final_correctness: int
    teacher_total: Optional[int] = None
    ai_feedback: str
    task_completeness_feedback: str
    code_quality_feedback: str
    correctness_feedback: str
    modified_by_teacher: Optional[datetime] = None

    class Config:
        from_attributes = True