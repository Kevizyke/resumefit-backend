from fastapi import FastAPI
from app.routers import auth, resumes

app = FastAPI(title="ResumeFit API")

app.include_router(auth.router)
app.include_router(resumes.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}