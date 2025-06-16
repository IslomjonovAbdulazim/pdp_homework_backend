from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    points = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, nullable=False)
    line_limit = Column(Integer, nullable=False)  # 300, 600, 900, 1200
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    file_extension = Column(String, nullable=False)  # .py, .dart, etc.
    ai_grading_prompt = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    teacher = relationship("User", back_populates="created_homework", foreign_keys=[teacher_id])
    group = relationship("Group", back_populates="homework")
    submissions = relationship("Submission", back_populates="homework")