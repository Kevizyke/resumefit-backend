import io
import pdfplumber
from fastapi import HTTPException, status

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2MB
PDF_MAGIC_BYTES = b"%PDF-"

def validate_pdf_upload(file_bytes: bytes, content_type: str, filename: str) -> None:
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a .pdf extension",
        )

    if content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF (invalid content type)",
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File exceeds maximum size of 2MB",
        )

    if not file_bytes.startswith(PDF_MAGIC_BYTES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not match a valid PDF",
        )


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_chunks = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not parse PDF — file may be corrupted or scanned as an image",
        )

    extracted_text = "\n".join(text_chunks).strip()

    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No extractable text found in PDF — it may be a scanned image without OCR",
        )

    return extracted_text