from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)

    # AI scores (original, never change)
    ai_task_completeness = Column(Integer, nullable=False)
    ai_code_quality = Column(Integer, nullable=False)
    ai_correctness = Column(Integer, nullable=False)
    ai_total = Column(Integer, nullable=False)

    # Final scores (editable by teacher)
    final_task_completeness = Column(Integer, nullable=False)
    final_code_quality = Column(Integer, nullable=False)
    final_correctness = Column(Integer, nullable=False)
    teacher_total = Column(Integer, nullable=True)  # Only if modified

    # Feedback
    ai_feedback = Column(Text, nullable=False)  # Short overall feedback
    task_completeness_feedback = Column(Text, nullable=False)
    code_quality_feedback = Column(Text, nullable=False)
    correctness_feedback = Column(Text, nullable=False)

    modified_by_teacher = Column(DateTime, nullable=True)  # When teacher changed grade

    # Relationships
    submission = relationship("Submission", back_populates="grade")