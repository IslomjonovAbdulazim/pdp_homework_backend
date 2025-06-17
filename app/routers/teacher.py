from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..dependencies.auth import get_current_teacher
from ..schemas.homework import HomeworkCreate, HomeworkUpdate, HomeworkResponse
from ..schemas.submission import SubmissionResponse
from ..schemas.grade import GradeUpdate, GradeResponse
from ..schemas.group import GroupResponse
from ..services.homework_service import HomeworkService
from ..services.grade_service import GradeService
from ..models.user import User
from ..models.group import Group

router = APIRouter()


# Homework CRUD
@router.get("/homework", response_model=List[HomeworkResponse])
async def get_homework(
        current_user: User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Get all homework created by the teacher"""

    homework_list = HomeworkService.get_teacher_homework(db, current_user.id)

    response_data = []
    for hw in homework_list:
        # Count submissions
        from ..models.submission import Submission
        submission_count = db.query(Submission).filter(
            Submission.homework_id == hw.id
        ).count()

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
            "teacher_name": current_user.fullname,
            "group_name": hw.group.name if hw.group else None,
            "submission_count": submission_count
        }
        response_data.append(HomeworkResponse(**hw_dict))

    return response_data


@router.post("/homework", response_model=HomeworkResponse)
async def create_homework(
        homework_data: HomeworkCreate,
        current_user: User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Create new homework"""

    homework = HomeworkService.create_homework(db, homework_data, current_user.id)

    return HomeworkResponse(
        id=homework.id,
        title=homework.title,
        description=homework.description,
        points=homework.points,
        start_date=homework.start_date,
        deadline=homework.deadline,
        line_limit=homework.line_limit,
        file_extension=homework.file_extension,
        teacher_id=homework.teacher_id,
        group_id=homework.group_id,
        created_at=homework.created_at,
        teacher_name=current_user.fullname,
        group_name=homework.group.name if homework.group else None,
        submission_count=0
    )


@router.put("/homework/{homework_id}", response_model=HomeworkResponse)
async def update_homework(
        homework_id: int,
        homework_data: HomeworkUpdate,
        current_user: User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Update existing homework"""

    homework = HomeworkService.update_homework(db, homework_id, homework_data, current_user.id)

    if not homework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework not found or you don't have access"
        )

    # Count submissions
    from ..models.submission import Submission
    submission_count = db.query(Submission).filter(
        Submission.homework_id == homework.id
    ).count()

    return HomeworkResponse(
        id=homework.id,
        title=homework.title,
        description=homework.description,
        points=homework.points,
        start_date=homework.start_date,
        deadline=homework.deadline,
        line_limit=homework.line_limit,
        file_extension=homework.file_extension,
        teacher_id=homework.teacher_id,
        group_id=homework.group_id,
        created_at=homework.created_at,
        teacher_name=current_user.fullname,
        group_name=homework.group.name if homework.group else None,
        submission_count=submission_count
    )


@router.delete("/homework/{homework_id}")
async def delete_homework(
        homework_id: int,
        current_user: User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Delete homework"""

    success = HomeworkService.delete_homework(db, homework_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework not found or you don't have access"
        )

    return {"message": "Homework deleted successfully"}


# Group management
@router.get("/groups", response_model=List[GroupResponse])
async def get_teacher_groups(
        current_user: User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Get groups assigned to the teacher"""

    groups = db.query(Group).filter(Group.teacher_id == current_user.id).all()

    response_data = []
    for group in groups:
        # Count students
        student_count = db.query(User).filter(User.group_id == group.id).count()

        response_data.append(GroupResponse(
            id=group.id,
            name=group.name,
            teacher_id=group.teacher_id,
            created_at=group.created_at,
            teacher_name=current_user.fullname,
            student_count=student_count
        ))

    return response_data


@router.get("/groups/{group_id}/submissions", response_model=List[SubmissionResponse])
async def get_group_submissions(
        group_id: int,
        homework_id: Optional[int] = None,
        current_user: User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Get all submissions for a group"""

    submissions = GradeService.get_group_submissions(
        db, group_id, current_user.id, homework_id
    )

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
            student_name=submission.student.fullname if submission.student else None,
            files=[]  # Files can be loaded separately if needed
        ))

    return response_data


@router.get("/groups/{group_id}/leaderboard")
async def get_group_leaderboard(
        group_id: int,
        period: str = "all",
        current_user: User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Get leaderboard for a group"""

    # Verify teacher has access to this group
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.teacher_id == current_user.id
    ).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found or you don't have access"
        )

    if period not in ["day", "week", "month", "all"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period must be one of: day, week, month, all"
        )

    leaderboard = GradeService.get_group_leaderboard(db, group_id, period)

    return {
        "group_id": group_id,
        "group_name": group.name,
        "period": period,
        "leaderboard": leaderboard
    }


# Grade management
@router.put("/submissions/{submission_id}/grade", response_model=GradeResponse)
async def update_grade(
        submission_id: int,
        grade_data: GradeUpdate,
        current_user: User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Update/override AI grade for a submission"""

    grade = GradeService.update_grade(db, submission_id, grade_data, current_user.id)

    return GradeResponse.from_orm(grade)


@router.get("/submissions/{submission_id}/grade", response_model=GradeResponse)
async def get_submission_grade(
        submission_id: int,
        current_user: User = Depends(get_current_teacher),
        db: Session = Depends(get_db)
):
    """Get detailed grade information for a submission"""

    # Verify teacher has access to this submission
    from ..models.submission import Submission
    submission = db.query(Submission).join(
        Submission.homework
    ).filter(
        Submission.id == submission_id
    ).first()

    if not submission or submission.homework.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or you don't have access"
        )

    grade = GradeService.get_grade_by_submission(db, submission_id)
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )

    return GradeResponse.from_orm(grade)