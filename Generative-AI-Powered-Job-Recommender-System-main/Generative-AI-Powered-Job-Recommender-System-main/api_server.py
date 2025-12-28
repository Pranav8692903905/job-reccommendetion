import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
from src.helper import extract_text_from_pdf, extract_keywords as local_extract_keywords, analyze_resume as run_analysis
from src.job_api import fetch_rss_jobs

app = FastAPI(title="Job Recommender API", version="0.3.0")

# Allow local dev frontend; adjust origins as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class KeywordsIn(BaseModel):
    summary: str

class Job(BaseModel):
    title: str
    companyName: str
    location: Optional[str] = None
    url: Optional[str] = None   # Primary link
    source: Optional[str] = None

class AnalysisOut(BaseModel):
    summary: str
    gaps: str
    roadmap: str

class JobsOut(BaseModel):
    jobs: List[Job]

@app.post("/api/analyze/resume", response_model=AnalysisOut)
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    data = await file.read()

    class _U:
        def __init__(self, b: bytes):
            self._b = b
        def read(self):
            return self._b

    resume_text = extract_text_from_pdf(_U(data))
    summary, gaps, roadmap = run_analysis(resume_text)
    return AnalysisOut(summary=summary, gaps=gaps, roadmap=roadmap)

@app.post("/api/keywords")
async def extract_keywords(body: KeywordsIn):
    keywords, _ = local_extract_keywords(body.summary, limit=12)
    return {"keywords": keywords}

@app.get("/api/jobs", response_model=JobsOut)
async def get_jobs(keywords: str, rows: int = 60):
    try:
        jobs = fetch_rss_jobs(keywords, rows=rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search failed: {e}")

    def map_job(j: dict) -> Job:
        return Job(
            title=j.get("title", ""),
            companyName=j.get("companyName", ""),
            location=j.get("location") or j.get("place") or j.get("city"),
            url=j.get("url") or j.get("link"),
            source=j.get("source"),
        )

    return JobsOut(jobs=[map_job(j) for j in jobs])

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "ok", "service": "Job Recommender API", "docs": "/docs"}

@app.get("/favicon.ico")
async def favicon():
    # Avoid noisy 404s from browser favicon requests
    return Response(status_code=204)
