from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse
from app.services.pdf_parser import validate_pdf_upload, extract_text_from_pdf

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_bytes = await file.read()

    validate_pdf_upload(
        file_bytes=file_bytes,
        content_type=file.content_type,
        filename=file.filename,
    )

    extracted_text = extract_text_from_pdf(file_bytes)

    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        extracted_text=extracted_text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume