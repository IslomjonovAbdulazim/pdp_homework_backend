from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum("admin", "teacher", "student", name="user_roles"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    group = relationship("Group", back_populates="students", foreign_keys=[group_id])
    sessions = relationship("Session", back_populates="user")
    submissions = relationship("Submission", back_populates="student")
    taught_groups = relationship("Group", back_populates="teacher", foreign_keys="Group.teacher_id")
    created_homework = relationship("Homework", back_populates="teacher")