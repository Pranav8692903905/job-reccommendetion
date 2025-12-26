# Job Recommender API (FastAPI)

A lightweight API wrapper over existing functions (`extract_text_from_pdf`, `ask_openai`, `fetch_linkedin_jobs`, `fetch_naukri_jobs`). Streamlit remains unchanged.

## Endpoints
- `POST /api/analyze/resume` (multipart, field `file`): returns `{ summary, gaps, roadmap }`
- `POST /api/keywords` with JSON `{ summary }`: returns `{ keywords }`
- `GET /api/jobs?keywords=...&rows=60`: returns `{ linkedinJobs: Job[], naukriJobs: Job[] }`
- `GET /api/health`: health check

## Run locally

```bash
# from repo root
cd Generative-AI-Powered-Job-Recommender-System-main/Generative-AI-Powered-Job-Recommender-System-main
python -m pip install -r requirements.txt
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

Set environment variables (e.g. `OPENAI_API_KEY`, `APIFY_API_TOKEN`) via `.env` in this folder.
