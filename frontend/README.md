# Job Recommender Frontend (React + TS)

This is a React + TypeScript frontend that mirrors the original Streamlit UI. It runs with mocked APIs by default so you can test the UI without any backend changes.

## Quickstart

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## API Wiring
- By default, `VITE_USE_MOCK=true` (no backend required).
- To connect to a Python API later, set `VITE_USE_MOCK=false` in a `.env` file and ensure a server is running on `http://localhost:8000` with routes:
  - `POST /api/analyze/resume` (multipart form with `file`) → `{ summary, gaps, roadmap }`
  - `POST /api/keywords` (JSON `{ summary }`) → `{ keywords: string }`
  - `GET /api/jobs?keywords=...` → `{ linkedinJobs: Job[], naukriJobs: Job[] }`

The UI will then use the real endpoints through the Vite dev server proxy.

## Scripts
- `npm run dev`: Run dev server
- `npm run build`: Build for production
- `npm run preview`: Preview production build
