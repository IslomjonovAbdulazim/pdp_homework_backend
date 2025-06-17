from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from fastapi import HTTPException, status
from ..models.grade import Grade
from ..models.submission import Submission
from ..models.homework import Homework
from ..models.user import User
from ..schemas.grade import GradeUpdate


class GradeService:
    @staticmethod
    def get_grade_by_submission(db: Session, submission_id: int) -> Optional[Grade]:
        """Get grade by submission ID"""
        return db.query(Grade).filter(Grade.submission_id == submission_id).first()

    @staticmethod
    def update_grade(
            db: Session,
            submission_id: int,
            grade_data: GradeUpdate,
            teacher_id: int
    ) -> Optional[Grade]:
        """Update grade scores (teacher override)"""

        # Get submission and verify teacher access
        submission = db.query(Submission).options(
            joinedload(Submission.homework)
        ).filter(Submission.id == submission_id).first()

        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )

        if submission.homework.teacher_id != teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this submission"
            )

        # Get grade record
        grade = db.query(Grade).filter(Grade.submission_id == submission_id).first()
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade record not found"
            )

        # Update scores
        updated = False
        for field, value in grade_data.dict(exclude_unset=True).items():
            if value is not None:
                setattr(grade, field, value)
                updated = True

        if updated:
            # Calculate new teacher total
            grade.teacher_total = (
                                          grade.final_task_completeness +
                                          grade.final_code_quality +
                                          grade.final_correctness
                                  ) // 3

            # Update submission final grade
            submission.final_grade = grade.teacher_total
            grade.modified_by_teacher = datetime.utcnow()

            db.commit()
            db.refresh(grade)

        return grade

    @staticmethod
    def get_group_leaderboard(
            db: Session,
            group_id: int,
            period: str = "all"
    ) -> List[dict]:
        """Get leaderboard for a group"""

        # Calculate time filter
        time_filter = None
        now = datetime.utcnow()

        if period == "day":
            time_filter = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            days_since_monday = now.weekday()
            time_filter = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        elif period == "month":
            time_filter = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Build query
        query = db.query(
            User.id,
            User.fullname,
            func.sum(Submission.final_grade).label('total_points'),
            func.count(Submission.id).label('submission_count')
        ).join(
            Submission, User.id == Submission.student_id
        ).join(
            Homework, Submission.homework_id == Homework.id
        ).filter(
            User.group_id == group_id
        )

        if time_filter:
            query = query.filter(Submission.submitted_at >= time_filter)

        results = query.group_by(User.id, User.fullname).order_by(
            desc('total_points')
        ).all()

        # Format leaderboard
        leaderboard = []
        for rank, result in enumerate(results, 1):
            leaderboard.append({
                "rank": rank,
                "student_id": result.id,
                "student_name": result.fullname,
                "total_points": result.total_points or 0,
                "submission_count": result.submission_count
            })

        return leaderboard

    @staticmethod
    def get_student_submissions(
            db: Session,
            student_id: int,
            limit: int = 20
    ) -> List[Submission]:
        """Get student's recent submissions with grades"""
        return db.query(Submission).options(
            joinedload(Submission.homework),
            joinedload(Submission.grade)
        ).filter(
            Submission.student_id == student_id
        ).order_by(
            desc(Submission.submitted_at)
        ).limit(limit).all()

    @staticmethod
    def get_group_submissions(
            db: Session,
            group_id: int,
            teacher_id: int,
            homework_id: Optional[int] = None
    ) -> List[Submission]:
        """Get all submissions for a group (teacher view)"""

        query = db.query(Submission).options(
            joinedload(Submission.student),
            joinedload(Submission.homework),
            joinedload(Submission.grade)
        ).join(
            Homework, Submission.homework_id == Homework.id
        ).filter(
            and_(
                Homework.group_id == group_id,
                Homework.teacher_id == teacher_id
            )
        )

        if homework_id:
            query = query.filter(Submission.homework_id == homework_id)

        return query.order_by(desc(Submission.submitted_at)).all()