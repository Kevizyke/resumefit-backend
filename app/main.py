from fastapi import FastAPI
from app.routers import auth, resumes, match_reports

app = FastAPI(title="ResumeFit API")

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(match_reports.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}