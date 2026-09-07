from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base

class MatchReport(Base):
    __tablename__ = "match_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_title = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    match_score = Column(Integer, nullable=False)
    missing_skills = Column(JSON, nullable=False)
    interview_questions = Column(JSON, nullable=False)
    raw_json_response = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())