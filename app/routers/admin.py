from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..dependencies.auth import get_current_admin
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..schemas.group import GroupCreate, GroupUpdate, GroupResponse
from ..services.grade_service import GradeService
from ..models.user import User
from ..models.group import Group
from ..utils.security import get_password_hash

router = APIRouter()


# Teachers CRUD
@router.get("/teachers", response_model=List[UserResponse])
async def get_teachers(
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Get all teachers"""
    teachers = db.query(User).filter(User.role == "teacher").all()
    return [UserResponse.from_orm(teacher) for teacher in teachers]


@router.post("/teachers", response_model=UserResponse)
async def create_teacher(
        teacher_data: UserCreate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Create new teacher"""

    # Validate role
    if teacher_data.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'teacher'"
        )

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == teacher_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Create teacher
    teacher = User(
        fullname=teacher_data.fullname,
        username=teacher_data.username,
        password_hash=get_password_hash(teacher_data.password),
        role=teacher_data.role,
        group_id=teacher_data.group_id
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return UserResponse.from_orm(teacher)


@router.put("/teachers/{teacher_id}", response_model=UserResponse)
async def update_teacher(
        teacher_id: int,
        teacher_data: UserUpdate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Update teacher"""

    teacher = db.query(User).filter(
        User.id == teacher_id,
        User.role == "teacher"
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Update fields
    for field, value in teacher_data.dict(exclude_unset=True).items():
        if field == "password" and value:
            setattr(teacher, "password_hash", get_password_hash(value))
        elif value is not None:
            setattr(teacher, field, value)

    db.commit()
    db.refresh(teacher)

    return UserResponse.from_orm(teacher)


@router.delete("/teachers/{teacher_id}")
async def delete_teacher(
        teacher_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Delete teacher"""

    teacher = db.query(User).filter(
        User.id == teacher_id,
        User.role == "teacher"
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Check if teacher has assigned groups
    group_count = db.query(Group).filter(Group.teacher_id == teacher_id).count()
    if group_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete teacher with assigned groups"
        )

    db.delete(teacher)
    db.commit()

    return {"message": "Teacher deleted successfully"}


# Students CRUD
@router.get("/students", response_model=List[UserResponse])
async def get_students(
        group_id: int = None,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Get all students, optionally filtered by group"""

    query = db.query(User).filter(User.role == "student")

    if group_id:
        query = query.filter(User.group_id == group_id)

    students = query.all()
    return [UserResponse.from_orm(student) for student in students]


@router.post("/students", response_model=UserResponse)
async def create_student(
        student_data: UserCreate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Create new student"""

    # Validate role
    if student_data.role != "student":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'student'"
        )

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == student_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Validate group if provided
    if student_data.group_id:
        group = db.query(Group).filter(Group.id == student_data.group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group not found"
            )

    # Create student
    student = User(
        fullname=student_data.fullname,
        username=student_data.username,
        password_hash=get_password_hash(student_data.password),
        role=student_data.role,
        group_id=student_data.group_id
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return UserResponse.from_orm(student)


@router.put("/students/{student_id}", response_model=UserResponse)
async def update_student(
        student_id: int,
        student_data: UserUpdate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Update student"""

    student = db.query(User).filter(
        User.id == student_id,
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Validate group if provided
    if student_data.group_id:
        group = db.query(Group).filter(Group.id == student_data.group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group not found"
            )

    # Update fields
    for field, value in student_data.dict(exclude_unset=True).items():
        if field == "password" and value:
            setattr(student, "password_hash", get_password_hash(value))
        elif value is not None:
            setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return UserResponse.from_orm(student)


@router.delete("/students/{student_id}")
async def delete_student(
        student_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Delete student"""

    student = db.query(User).filter(
        User.id == student_id,
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Check if student has submissions
    from ..models.submission import Submission
    submission_count = db.query(Submission).filter(Submission.student_id == student_id).count()
    if submission_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete student with submissions"
        )

    db.delete(student)
    db.commit()

    return {"message": "Student deleted successfully"}


# Groups CRUD
@router.get("/groups", response_model=List[GroupResponse])
async def get_groups(
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Get all groups"""

    groups = db.query(Group).all()

    response_data = []
    for group in groups:
        # Count students
        student_count = db.query(User).filter(User.group_id == group.id).count()

        # Get teacher name
        teacher_name = None
        if group.teacher:
            teacher_name = group.teacher.fullname

        response_data.append(GroupResponse(
            id=group.id,
            name=group.name,
            teacher_id=group.teacher_id,
            created_at=group.created_at,
            teacher_name=teacher_name,
            student_count=student_count
        ))

    return response_data


@router.post("/groups", response_model=GroupResponse)
async def create_group(
        group_data: GroupCreate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Create new group"""

    # Validate teacher
    teacher = db.query(User).filter(
        User.id == group_data.teacher_id,
        User.role == "teacher"
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher not found"
        )

    # Create group
    group = Group(
        name=group_data.name,
        teacher_id=group_data.teacher_id
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        teacher_id=group.teacher_id,
        created_at=group.created_at,
        teacher_name=teacher.fullname,
        student_count=0
    )


@router.put("/groups/{group_id}", response_model=GroupResponse)
async def update_group(
        group_id: int,
        group_data: GroupUpdate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Update group"""

    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Validate teacher if provided
    if group_data.teacher_id:
        teacher = db.query(User).filter(
            User.id == group_data.teacher_id,
            User.role == "teacher"
        ).first()

        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher not found"
            )

    # Update fields
    for field, value in group_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(group, field, value)

    db.commit()
    db.refresh(group)

    # Get updated info
    student_count = db.query(User).filter(User.group_id == group.id).count()
    teacher_name = group.teacher.fullname if group.teacher else None

    return GroupResponse(
        id=group.id,
        name=group.name,
        teacher_id=group.teacher_id,
        created_at=group.created_at,
        teacher_name=teacher_name,
        student_count=student_count
    )


@router.delete("/groups/{group_id}")
async def delete_group(
        group_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Delete group"""

    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Check if group has students
    student_count = db.query(User).filter(User.group_id == group_id).count()
    if student_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete group with assigned students"
        )

    # Check if group has homework
    from ..models.homework import Homework
    homework_count = db.query(Homework).filter(Homework.group_id == group_id).count()
    if homework_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete group with assigned homework"
        )

    db.delete(group)
    db.commit()

    return {"message": "Group deleted successfully"}


# Group management
@router.put("/students/{student_id}/group")
async def move_student_to_group(
        student_id: int,
        group_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Move student to different group"""

    # Get student
    student = db.query(User).filter(
        User.id == student_id,
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Validate group
    if group_id:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group not found"
            )

    # Update student group
    student.group_id = group_id
    db.commit()

    return {"message": f"Student moved to group {group_id}" if group_id else "Student removed from group"}


@router.put("/groups/{group_id}/teacher")
async def assign_teacher_to_group(
        group_id: int,
        teacher_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Assign teacher to group"""

    # Get group
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Validate teacher
    teacher = db.query(User).filter(
        User.id == teacher_id,
        User.role == "teacher"
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher not found"
        )

    # Update group teacher
    group.teacher_id = teacher_id
    db.commit()

    return {"message": f"Teacher {teacher.fullname} assigned to group {group.name}"}


@router.get("/groups/{group_id}/leaderboard")
async def get_group_leaderboard(
        group_id: int,
        period: str = "all",
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Get leaderboard for any group (admin view)"""

    # Verify group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
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