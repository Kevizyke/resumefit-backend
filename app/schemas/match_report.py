from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class MatchReportLLMOutput(BaseModel):
    """Schema the LLM's response must conform to."""
    match_score: int = Field(ge=0, le=100, description="Match score from 0-100")
    found_skills: list[str] = Field(description="Skills found in the resume that match the job")
    missing_skills: list[str] = Field(description="Skills in the job description missing from the resume")
    suggestions: list[str] = Field(description="Concrete suggestions to improve the resume for this job")
    interview_questions: list[str] = Field(description="Likely interview questions based on the gaps found")


class MatchReportRequest(BaseModel):
    resume_id: int
    job_title: str
    company_name: str | None = None
    job_description: str


class MatchReportResponse(BaseModel):
    id: int
    job_title: str
    company_name: str | None
    match_score: int
    missing_skills: list
    interview_questions: list
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)