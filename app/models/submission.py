from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homework.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    ai_grade = Column(Integer, nullable=False)  # Original AI score
    final_grade = Column(Integer, nullable=False)  # Final score (shown to student)
    ai_feedback = Column(Text, nullable=False)  # Short overall feedback
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    homework = relationship("Homework", back_populates="submissions")
    student = relationship("User", back_populates="submissions")
    files = relationship("SubmissionFile", back_populates="submission")
    grade = relationship("Grade", back_populates="submission", uselist=False)


class SubmissionFile(Base):
    __tablename__ = "submission_files"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    file_name = Column(Text, nullable=False)
    content = Column(Text, nullable=False)  # Code content as string
    line_count = Column(Integer, nullable=False)

    # Relationships
    submission = relationship("Submission", back_populates="files")