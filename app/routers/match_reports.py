from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.match_report import MatchReport
from app.schemas.match_report import MatchReportRequest, MatchReportResponse
from app.services.ai_matcher import get_match_report
from app.services.rate_limit import enforce_rate_limit

router = APIRouter(prefix="/api/v1/match-reports", tags=["match-reports"])

@router.post(
    "",
    response_model=MatchReportResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_rate_limit)],
)
def create_match_report(
    request: MatchReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = (
        db.query(Resume)
        .filter(Resume.id == request.resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    llm_result = get_match_report(
        resume_text=resume.extracted_text,
        job_description=request.job_description,
    )

    match_report = MatchReport(
        user_id=current_user.id,
        resume_id=resume.id,
        job_title=request.job_title,
        company_name=request.company_name,
        match_score=llm_result.match_score,
        missing_skills=llm_result.missing_skills,
        interview_questions=llm_result.interview_questions,
        raw_json_response=llm_result.model_dump(),
    )
    db.add(match_report)
    db.commit()
    db.refresh(match_report)

    return match_report