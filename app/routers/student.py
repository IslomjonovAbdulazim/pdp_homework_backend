from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..dependencies.auth import get_current_student
from ..schemas.homework import HomeworkResponse
from ..schemas.submission import SubmissionCreate, SubmissionResponse
from ..schemas.grade import GradeResponse
from ..services.homework_service import HomeworkService
from ..services.grade_service import GradeService
from ..models.user import User

router = APIRouter()


@router.get("/leaderboard")
async def get_leaderboard(
        period: str = "all",
        current_user: User = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    """Get leaderboard for student's group"""

    if not current_user.group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not assigned to any group"
        )

    if period not in ["day", "week", "month", "all"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period must be one of: day, week, month, all"
        )

    leaderboard = GradeService.get_group_leaderboard(
        db, current_user.group_id, period
    )

    return {
        "group_id": current_user.group_id,
        "period": period,
        "leaderboard": leaderboard
    }


@router.get("/homework", response_model=List[HomeworkResponse])
async def get_available_homework(
        current_user: User = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    """Get available homework for student"""

    homework_list = HomeworkService.get_student_homework(db, current_user.id)

    # Convert to response format
    response_data = []
    for hw in homework_list:
        hw_dict = {
            "id": hw.id,
            "title": hw.title,
            "description": hw.description,
            "points": hw.points,
            "start_date": hw.start_date,
            "deadline": hw.deadline,
            "line_limit": hw.line_limit,
            "file_extension": hw.file_extension,
            "teacher_id": hw.teacher_id,
            "group_id": hw.group_id,
            "created_at": hw.created_at,
            "teacher_name": hw.teacher.fullname if hw.teacher else None,
            "group_name": hw.group.name if hw.group else None,
            "submission_count": 0  # Not needed for student view
        }
        response_data.append(HomeworkResponse(**hw_dict))

    return response_data


@router.post("/homework/{homework_id}/submit", response_model=SubmissionResponse)
async def submit_homework(
        homework_id: int,
        submission_data: SubmissionCreate,
        current_user: User = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    """Submit homework solution"""

    homework_service = HomeworkService()

    # Convert submission data to the format expected by the service
    files_data = [
        {
            "file_name": file.file_name,
            "content": file.content
        } for file in submission_data.files
    ]

    try:
        submission = await homework_service.submit_homework(
            db, homework_id, current_user.id, files_data
        )

        # Return response
        return SubmissionResponse(
            id=submission.id,
            homework_id=submission.homework_id,
            student_id=submission.student_id,
            submitted_at=submission.submitted_at,
            ai_grade=submission.ai_grade,
            final_grade=submission.final_grade,
            ai_feedback=submission.ai_feedback,
            homework_title=submission.homework.title if submission.homework else None,
            student_name=current_user.fullname,
            files=[]  # Files can be loaded separately if needed
        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit homework: {str(e)}"
        )


@router.get("/submissions", response_model=List[SubmissionResponse])
async def get_submissions(
        limit: int = 20,
        current_user: User = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    """Get student's submission history"""

    submissions = GradeService.get_student_submissions(db, current_user.id, limit)

    response_data = []
    for submission in submissions:
        response_data.append(SubmissionResponse(
            id=submission.id,
            homework_id=submission.homework_id,
            student_id=submission.student_id,
            submitted_at=submission.submitted_at,
            ai_grade=submission.ai_grade,
            final_grade=submission.final_grade,
            ai_feedback=submission.ai_feedback,
            homework_title=submission.homework.title if submission.homework else None,
            student_name=current_user.fullname,
            files=[]  # Files can be loaded separately if needed
        ))

    return response_data


@router.get("/submissions/{submission_id}/grade", response_model=GradeResponse)
async def get_submission_grade(
        submission_id: int,
        current_user: User = Depends(get_current_student),
        db: Session = Depends(get_db)
):
    """Get detailed grade information for a submission"""

    # Verify submission belongs to current student
    from ..models.submission import Submission
    submission = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.student_id == current_user.id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    grade = GradeService.get_grade_by_submission(db, submission_id)
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )

    return GradeResponse.from_orm(grade)