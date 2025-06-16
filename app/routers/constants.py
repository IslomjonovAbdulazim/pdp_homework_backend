from fastapi import APIRouter
from ..utils.constants import (
    LINE_LIMIT_OPTIONS,
    FILE_EXTENSION_OPTIONS,
    MAX_FILES_PER_HOMEWORK,
    MAX_LINES_PER_FILE,
    MAX_SESSIONS_PER_USER,
    GRADING_RUBRICS
)

router = APIRouter()

@router.get("/constants")
async def get_constants():
    """Get all app constants"""
    return {
        "line_limit_options": LINE_LIMIT_OPTIONS,
        "file_extension_options": FILE_EXTENSION_OPTIONS,
        "max_files_per_homework": MAX_FILES_PER_HOMEWORK,
        "max_lines_per_file": MAX_LINES_PER_FILE,
        "max_sessions_per_user": MAX_SESSIONS_PER_USER,
        "grading_rubrics": GRADING_RUBRICS
    }