# Job Recommender - Setup Guide

## Architecture
- **Frontend**: React + TypeScript + Vite (port 5173)
- **Backend**: FastAPI + Python (port 8000)
- **Analysis**: Local heuristics or OpenRouter (optional)
- **Jobs**: RSS feeds (WeWorkRemotely, Remotive)

## Quick Start

### 1. Start Backend (Terminal 1)
```bash
cd Generative-AI-Powered-Job-Recommender-System-main/Generative-AI-Powered-Job-Recommender-System-main
pip install -r requirements.txt
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

Backend should show:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

Frontend should show:
```
VITE v6.4.1  ready in XXX ms
➜  Local:   http://localhost:5173/
```

### 3. Open App
Visit: http://localhost:5173

## Troubleshooting

### "Failed to analyze resume" Error

**Check 1: Is backend running?**
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"ok"}
```

**Check 2: Is frontend running?**
```bash
curl http://localhost:5173/
# Should return HTML
```

**Check 3: Test backend directly**
```bash
# Create test PDF
python - << 'PY'
import fitz
doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 72), "Test Resume\nSkills: Python", fontsize=12)
doc.save("/tmp/test.pdf")
PY

# Test analyze endpoint
curl -F "file=@/tmp/test.pdf" http://localhost:8000/api/analyze/resume
# Should return JSON with summary, gaps, roadmap
```

**Check 4: Test through frontend proxy**
```bash
curl -F "file=@/tmp/test.pdf" http://localhost:5173/api/analyze/resume
# Should return same JSON as above
```

**Check 5: Browser console**
- Open http://localhost:5173
- Open DevTools (F12)
- Go to Console tab
- Try uploading a PDF
- Look for detailed error messages

### Common Issues

1. **Port already in use**
   ```bash
   # Kill process on port 8000
   lsof -ti:8000 | xargs kill
   
   # Kill process on port 5173
   lsof -ti:5173 | xargs kill
   ```

2. **Module not found**
   ```bash
   # Backend
   cd Generative-AI-Powered-Job-Recommender-System-main/Generative-AI-Powered-Job-Recommender-System-main
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

3. **CORS errors**
   - Backend already has CORS middleware configured
   - Vite proxy forwards /api/* to http://localhost:8000
   - If still seeing CORS, check both services are running

## Optional: OpenRouter Enhancement

For better analysis quality, set OpenRouter API key:

```bash
cd Generative-AI-Powered-Job-Recommender-System-main/Generative-AI-Powered-Job-Recommender-System-main
echo "OPENROUTER_API_KEY=your_key_here" > .env
```

Without this key, the system uses heuristic analysis (no API required).

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/analyze/resume` - Upload PDF, get analysis
- `POST /api/keywords` - Extract keywords from summary
- `GET /api/jobs?keywords=...` - Get RSS job listings

## Tech Stack Details

**Frontend:**
- React 18
- TypeScript
- Vite 6
- Axios for API calls
- Custom gradient UI with glassmorphism

**Backend:**
- FastAPI
- PyMuPDF for PDF parsing
- feedparser for RSS jobs
- Optional: OpenRouter for LLM analysis
