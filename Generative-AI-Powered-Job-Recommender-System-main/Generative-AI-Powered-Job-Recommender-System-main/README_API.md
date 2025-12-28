# Job Recommender API (FastAPI)

API wrapper over local analysis utilities (`extract_text_from_pdf`, `analyze_resume`, `extract_keywords`) and RSS-based job fetching.

## Endpoints
- `POST /api/analyze/resume` (multipart, field `file`): returns `{ summary, gaps, roadmap }`
- `POST /api/keywords` with JSON `{ summary }`: returns `{ keywords }`
- `GET /api/jobs?keywords=...&rows=60`: returns `{ jobs: Job[] }`
- `GET /api/health`: health check

## Run locally

```bash
# from repo root
cd Generative-AI-Powered-Job-Recommender-System-main/Generative-AI-Powered-Job-Recommender-System-main
python -m pip install -r requirements.txt
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

Optional: set `OPENROUTER_API_KEY` (and `OPENROUTER_MODEL`) for LLM-powered analysis. Without it, heuristic analysis runs. No external job APIs required (RSS feeds only).
