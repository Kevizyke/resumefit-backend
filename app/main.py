from fastapi import FastAPI

app = FastAPI(title="ResumeFit API")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status":"ok"}