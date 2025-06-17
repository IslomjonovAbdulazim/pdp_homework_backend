from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from ..models.homework import Homework
from ..models.submission import Submission, SubmissionFile
from ..models.grade import Grade
from ..models.user import User
from ..models.group import Group
from ..schemas.homework import HomeworkCreate, HomeworkUpdate
from .ai_service import AIService


class HomeworkService:
    def __init__(self):
        self.ai_service = AIService()

    @staticmethod
    def get_homework_by_id(db: Session, homework_id: int, user_id: int = None, role: str = None) -> Optional[Homework]:
        """Get homework by ID with access control"""
        query = db.query(Homework).options(
            joinedload(Homework.teacher),
            joinedload(Homework.group)
        )

        homework = query.filter(Homework.id == homework_id).first()

        if not homework:
            return None

        # Access control
        if role == "teacher" and homework.teacher_id != user_id:
            return None
        elif role == "student":
            # Student can only see homework for their group
            student = db.query(User).filter(User.id == user_id).first()
            if not student or student.group_id != homework.group_id:
                return None

        return homework

    @staticmethod
    def get_teacher_homework(db: Session, teacher_id: int) -> List[Homework]:
        """Get all homework created by a teacher"""
        return db.query(Homework).options(
            joinedload(Homework.group)
        ).filter(Homework.teacher_id == teacher_id).all()

    @staticmethod
    def get_student_homework(db: Session, student_id: int) -> List[Homework]:
        """Get available homework for a student"""
        student = db.query(User).filter(User.id == student_id).first()
        if not student or not student.group_id:
            return []

        now = datetime.utcnow()

        return db.query(Homework).filter(
            and_(
                Homework.group_id == student.group_id,
                Homework.start_date <= now,
                Homework.deadline > now
            )
        ).all()

    @staticmethod
    def create_homework(db: Session, homework_data: HomeworkCreate, teacher_id: int) -> Homework:
        """Create new homework"""
        # Verify teacher has access to the group
        group = db.query(Group).filter(
            and_(
                Group.id == homework_data.group_id,
                Group.teacher_id == teacher_id
            )
        ).first()

        if not group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this group"
            )

        homework = Homework(
            **homework_data.dict(),
            teacher_id=teacher_id
        )

        db.add(homework)
        db.commit()
        db.refresh(homework)

        return homework

    @staticmethod
    def update_homework(db: Session, homework_id: int, homework_data: HomeworkUpdate, teacher_id: int) -> Optional[
        Homework]:
        """Update homework"""
        homework = db.query(Homework).filter(
            and_(
                Homework.id == homework_id,
                Homework.teacher_id == teacher_id
            )
        ).first()

        if not homework:
            return None

        # Update fields
        for field, value in homework_data.dict(exclude_unset=True).items():
            setattr(homework, field, value)

        db.commit()
        db.refresh(homework)

        return homework

    @staticmethod
    def delete_homework(db: Session, homework_id: int, teacher_id: int) -> bool:
        """Delete homework"""
        homework = db.query(Homework).filter(
            and_(
                Homework.id == homework_id,
                Homework.teacher_id == teacher_id
            )
        ).first()

        if not homework:
            return False

        # Check if there are submissions
        submission_count = db.query(Submission).filter(Submission.homework_id == homework_id).count()
        if submission_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete homework that has submissions"
            )

        db.delete(homework)
        db.commit()

        return True

    async def submit_homework(
            self,
            db: Session,
            homework_id: int,
            student_id: int,
            files_data: List[dict]
    ) -> Submission:
        """Submit homework with AI grading"""

        # Get homework and validate
        homework = self.get_homework_by_id(db, homework_id, student_id, "student")
        if not homework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Homework not found or not accessible"
            )

        # Check deadline
        if datetime.utcnow() > homework.deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Homework deadline has passed"
            )

        # Check if already submitted
        existing = db.query(Submission).filter(
            and_(
                Submission.homework_id == homework_id,
                Submission.student_id == student_id
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already submitted this homework"
            )

        # Validate total line count
        total_lines = sum(len(file_data["content"].split('\n')) for file_data in files_data)
        if total_lines > homework.line_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Total lines ({total_lines}) exceed limit ({homework.line_limit})"
            )

        # Create submission files
        submission_files = []
        for file_data in files_data:
            file_obj = SubmissionFile(
                file_name=file_data["file_name"],
                content=file_data["content"],
                line_count=len(file_data["content"].split('\n'))
            )
            submission_files.append(file_obj)

        # Get AI grading
        ai_grades = await self.ai_service.grade_submission(homework, submission_files)

        # Create submission
        submission = Submission(
            homework_id=homework_id,
            student_id=student_id,
            ai_grade=ai_grades["total"],
            final_grade=ai_grades["total"],
            ai_feedback=ai_grades["overall_feedback"]
        )

        db.add(submission)
        db.flush()  # Get submission ID

        # Add files to submission
        for file_obj in submission_files:
            file_obj.submission_id = submission.id
            db.add(file_obj)

        # Create detailed grade record
        grade = Grade(
            submission_id=submission.id,
            ai_task_completeness=ai_grades["task_completeness"],
            ai_code_quality=ai_grades["code_quality"],
            ai_correctness=ai_grades["correctness"],
            ai_total=ai_grades["total"],
            final_task_completeness=ai_grades["task_completeness"],
            final_code_quality=ai_grades["code_quality"],
            final_correctness=ai_grades["correctness"],
            ai_feedback=ai_grades["overall_feedback"],
            task_completeness_feedback=ai_grades["task_completeness_feedback"],
            code_quality_feedback=ai_grades["code_quality_feedback"],
            correctness_feedback=ai_grades["correctness_feedback"]
        )

        db.add(grade)
        db.commit()
        db.refresh(submission)

        return submission