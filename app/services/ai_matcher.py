import hashlib
import json
from google import genai
from fastapi import HTTPException, status
from redis import Redis
from app.config import settings
from app.schemas.match_report import MatchReportLLMOutput

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
genai_client = genai.Client(api_key=settings.gemini_api_key)

MODEL_NAME = "gemini-3.5-flash"
MAX_RETRIES = 2
CACHE_TTL_SECONDS = 60 * 60 * 24 * 7  # 1 week


def _build_cache_key(resume_text: str, job_description: str) -> str:
    combined = f"{resume_text}::{job_description}"
    digest = hashlib.sha256(combined.encode("utf-8")).hexdigest()
    return f"match_report:{digest}"


def _build_prompt(resume_text: str, job_description: str) -> str:
    return f"""You are an expert technical recruiter. Compare the resume below against the job description.

Extract:
- A match_score from 0-100 representing how well the resume fits the job.
- found_skills: skills/technologies present in the resume that are relevant to the job.
- missing_skills: skills/technologies the job asks for that are absent from the resume.
- suggestions: concrete, specific ways to improve the resume for this exact job.
- interview_questions: 3-5 realistic interview questions targeting the gaps you found.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""


def _call_gemini(prompt: str) -> MatchReportLLMOutput:
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = genai_client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": MatchReportLLMOutput,
                },
            )
            return MatchReportLLMOutput.model_validate_json(response.text)

        except Exception as e:
            last_error = e
            continue

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"AI service failed to return a valid response after {MAX_RETRIES + 1} attempts: {last_error}",
    )


def get_match_report(resume_text: str, job_description: str) -> MatchReportLLMOutput:
    cache_key = _build_cache_key(resume_text, job_description)

    cached = redis_client.get(cache_key)
    if cached:
        return MatchReportLLMOutput.model_validate_json(cached)

    prompt = _build_prompt(resume_text, job_description)
    result = _call_gemini(prompt)

    redis_client.setex(cache_key, CACHE_TTL_SECONDS, result.model_dump_json())

    return result