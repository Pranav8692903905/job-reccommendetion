import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from src.helper import extract_text_from_pdf, ask_openai
from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs

app = FastAPI(title="Job Recommender API", version="0.1.0")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

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
    link: Optional[str] = None  # LinkedIn
    url: Optional[str] = None   # Naukri

class AnalysisOut(BaseModel):
    summary: str
    gaps: str
    roadmap: str

class JobsOut(BaseModel):
    linkedinJobs: List[Job]
    naukriJobs: List[Job]

@app.post("/api/analyze/resume", response_model=AnalysisOut)
async def analyze_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    data = await file.read()

    class _U:
        def __init__(self, b: bytes):
            self._b = b
        def read(self):
            return self._b

    resume_text = extract_text_from_pdf(_U(data))

    if DEMO_MODE:
        return AnalysisOut(
            summary=(
                "Experienced Data Scientist with 5+ years in NLP and ML, proficient in Python, SQL,"
                " and cloud services. Delivered end-to-end ML systems and LLM-backed apps."
            ),
            gaps=(
                "Missing advanced MLOps exposure (Kubeflow), limited production-scale vector DB experience,"
                " and formal certifications in Azure or AWS ML."
            ),
            roadmap=(
                "1) Learn orchestration (Prefect/Kubeflow). 2) Earn AWS ML Specialty."
                " 3) Build a retrieval-augmented generation app with embeddings and evaluation."
            ),
        )

    try:
        summary = ask_openai(
            f"Summarize this resume highlighting the skills, edcucation, and experience: \n\n{resume_text}",
            max_tokens=500,
        )
        gaps = ask_openai(
            f"Analyze this resume and highlight missing skills, certifications, and experiences needed for better job opportunities: \n\n{resume_text}",
            max_tokens=400,
        )
        roadmap = ask_openai(
            f"Based on this resume, suggest a future roadmap to improve this person's career prospects (Skill to learn, certification needed, industry exposure): \n\n{resume_text}",
            max_tokens=400,
        )
        return AnalysisOut(summary=summary, gaps=gaps, roadmap=roadmap)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI call failed: {e}")

@app.post("/api/keywords")
async def extract_keywords(body: KeywordsIn):
    if DEMO_MODE:
        return {"keywords": "Data Scientist, NLP Engineer, LLM Engineer, Machine Learning Engineer"}
    try:
        keywords = ask_openai(
            (
                "Based on this resume summary, suggest the best job titles and keywords "
                "for searching jobs. Give a comma-separated list only, no explanation.\n\n"
                f"Summary: {body.summary}"
            ),
            max_tokens=100,
        )
        return {"keywords": keywords}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {e}")

@app.get("/api/jobs", response_model=JobsOut)
async def get_jobs(keywords: str, rows: int = 60):
    if DEMO_MODE:
        linkedin_jobs = [
            {"title": "Machine Learning Engineer", "companyName": "TechCorp", "location": "Remote", "link": "https://www.linkedin.com/jobs"},
            {"title": "NLP Engineer", "companyName": "LinguaAI", "location": "Bengaluru, IN", "link": "https://www.linkedin.com/jobs"},
        ]
        naukri_jobs = [
            {"title": "Data Scientist", "companyName": "AnalyticsHub", "location": "Pune, IN", "url": "https://www.naukri.com"},
            {"title": "LLM Engineer", "companyName": "ModelWorks", "location": "Hyderabad, IN", "url": "https://www.naukri.com"},
        ]
    else:
        try:
            linkedin_jobs = fetch_linkedin_jobs(keywords, rows=rows)
            naukri_jobs = fetch_naukri_jobs(keywords, rows=rows)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Job search failed: {e}")

    def map_job(j: dict) -> Job:
        return Job(
            title=j.get("title", ""),
            companyName=j.get("companyName", ""),
            location=j.get("location") or j.get("place") or j.get("city"),
            link=j.get("link"),
            url=j.get("url"),
        )

    return JobsOut(
        linkedinJobs=[map_job(j) for j in linkedin_jobs],
        naukriJobs=[map_job(j) for j in naukri_jobs],
    )

@app.get("/api/health")
async def health():
    return {"status": "ok"}
