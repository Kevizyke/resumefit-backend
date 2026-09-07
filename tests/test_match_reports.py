from unittest.mock import patch
from app.schemas.match_report import MatchReportLLMOutput


FAKE_LLM_RESULT = MatchReportLLMOutput(
    match_score=85,
    found_skills=["Python", "FastAPI"],
    missing_skills=["Kubernetes"],
    suggestions=["Highlight your Docker experience more prominently."],
    interview_questions=["How would you containerize this service?"],
)


def _upload_resume(client, auth_headers, sample_pdf_bytes):
    response = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
    )
    return response.json()["id"]


@patch("app.services.ai_matcher._call_gemini", return_value=FAKE_LLM_RESULT)
def test_create_match_report(mock_gemini, client, auth_headers, sample_pdf_bytes):
    resume_id = _upload_resume(client, auth_headers, sample_pdf_bytes)

    response = client.post(
        "/api/v1/match-reports",
        headers=auth_headers,
        json={
            "resume_id": resume_id,
            "job_title": "Backend Developer",
            "company_name": "Acme Corp",
            "job_description": "Looking for a Python/FastAPI developer with Kubernetes experience.",
        },
    )
    print("STATUS:", response.status_code)
    print("BODY:", response.json())
    print("RESUME_ID USED:", resume_id)
    assert response.status_code == 201
    data = response.json()
    assert data["match_score"] == 85
    mock_gemini.assert_called_once()


@patch("app.services.ai_matcher._call_gemini", return_value=FAKE_LLM_RESULT)
def test_match_report_uses_cache_on_second_call(mock_gemini, client, auth_headers, sample_pdf_bytes):
    resume_id = _upload_resume(client, auth_headers, sample_pdf_bytes)
    payload = {
        "resume_id": resume_id,
        "job_title": "Backend Developer",
        "company_name": "Acme Corp",
        "job_description": "Looking for a Python/FastAPI developer with Kubernetes experience.",
    }

    client.post("/api/v1/match-reports", headers=auth_headers, json=payload)
    client.post("/api/v1/match-reports", headers=auth_headers, json=payload)

    # If caching works, Gemini should only ever be called once for identical input
    mock_gemini.assert_called_once()


def test_match_report_for_nonexistent_resume_returns_404(client, auth_headers):
    response = client.post(
        "/api/v1/match-reports",
        headers=auth_headers,
        json={
            "resume_id": 999999,
            "job_title": "Backend Developer",
            "job_description": "Some job description.",
        },
    )
    assert response.status_code == 404