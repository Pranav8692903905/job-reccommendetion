import fitz  # PyMuPDF
from collections import Counter
import json
import os
import re
from typing import List, Tuple

import requests


STOPWORDS = {
    "and", "or", "the", "a", "an", "to", "of", "in", "on", "for", "with", "by", "from",
    "at", "as", "is", "are", "was", "were", "be", "this", "that", "it", "its", "your",
    "you", "we", "they", "their", "our", "have", "has", "had", "will", "can", "may",
    "pdf", "page", "pages"
}

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku-20240307")
OPENROUTER_SITE = os.getenv("OPENROUTER_SITE_URL", "http://localhost")
OPENROUTER_APP = os.getenv("OPENROUTER_APP_NAME", "job-recommender")


def extract_text_from_pdf(uploaded_file):
    """Extract text from a PDF upload without external APIs."""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = "".join(page.get_text() for page in doc)
    return text


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def summarize_resume(text: str, max_sentences: int = 3) -> str:
    sentences = _sentences(text)
    if not sentences:
        return "No readable text found in resume."
    return " ".join(sentences[:max_sentences])


def extract_keywords(text: str, limit: int = 10) -> Tuple[str, List[str]]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_+#/.-]{2,}", text.lower())
    tokens = [t for t in tokens if t not in STOPWORDS]
    counts = Counter(tokens)
    top = [w for w, _ in counts.most_common(limit)]
    return ", ".join(top), top


def detect_skill_gaps(tokens: List[str]) -> str:
    buckets = {
        "cloud": {"aws", "azure", "gcp"},
        "mlops": {"mlops", "kubeflow", "mlflow", "airflow", "prefect"},
        "data": {"sql", "warehouse", "snowflake", "bigquery", "redshift"},
        "llm": {"llm", "rag", "langchain", "llamaindex"},
    }

    missing = []
    token_set = set(tokens)
    for label, keywords in buckets.items():
        if token_set.isdisjoint(keywords):
            missing.append(label)

    if not missing:
        return "Solid coverage across cloud, data, MLOps, and LLM stacks."

    readable = {
        "cloud": "Cloud platforms (AWS/Azure/GCP)",
        "mlops": "MLOps tooling (Kubeflow/MLflow/Airflow)",
        "data": "Data warehousing and SQL depth",
        "llm": "LLM app patterns (RAG, LangChain, LlamaIndex)",
    }
    parts = [readable[m] for m in missing if m in readable]
    return "Needs evidence in: " + "; ".join(parts)


def build_roadmap(tokens: List[str]) -> str:
    roadmap_items = []
    token_set = set(tokens)

    if token_set.isdisjoint({"aws", "azure", "gcp"}):
        roadmap_items.append("Earn an associate-level cloud cert (AWS/GCP/Azure) and deploy a small service.")
    if token_set.isdisjoint({"mlops", "kubeflow", "mlflow", "airflow", "prefect"}):
        roadmap_items.append("Ship one end-to-end ML pipeline with orchestration (Prefect/Airflow) and experiment tracking (MLflow).")
    if token_set.isdisjoint({"sql", "warehouse", "snowflake", "bigquery", "redshift"}):
        roadmap_items.append("Improve SQL depth; model a dataset in a warehouse (Snowflake/BigQuery) with CI checks.")
    if token_set.isdisjoint({"llm", "rag", "langchain", "llamaindex"}):
        roadmap_items.append("Build a retrieval-augmented generation demo; evaluate responses with test cases.")

    if not roadmap_items:
        roadmap_items.append("Document and publish case studies of delivered projects to strengthen portfolio.")

    return "\n".join(f"- {item}" for item in roadmap_items)


def ask_openrouter(prompt: str, max_tokens: int = 500) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_SITE,
        "X-Title": OPENROUTER_APP,
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a concise resume analyst."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.4,
    }

    resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=40)
    if resp.status_code >= 400:
        raise RuntimeError(f"OpenRouter error {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def _analyze_with_openrouter(text: str) -> Tuple[str, str, str]:
    prompt = (
        "Analyze this resume text and reply as JSON with keys summary, gaps, roadmap. "
        "Summary should be 3 sentences. Gaps should list missing skills or areas. "
        "Roadmap should be 3 bullet points. Resume text:\n\n" + text
    )
    content = ask_openrouter(prompt, max_tokens=420)
    try:
        parsed = json.loads(content)
        return parsed.get("summary", ""), parsed.get("gaps", ""), parsed.get("roadmap", "")
    except Exception:
        # If not valid JSON, fall back to simple splitting
        parts = content.split("\n")
        summary = parts[0] if parts else content
        gaps = "; ".join(parts[1:3]) if len(parts) > 1 else ""
        roadmap = "\n".join(parts[3:]) if len(parts) > 3 else ""
        return summary, gaps, roadmap


def analyze_resume(text: str) -> Tuple[str, str, str]:
    text = text.strip()
    if not text:
        return "No readable text found in resume.", "", ""

    if OPENROUTER_API_KEY:
        try:
            return _analyze_with_openrouter(text)
        except Exception:
            pass  # fall back to heuristic path

    summary = summarize_resume(text)
    _, tokens = extract_keywords(text, limit=30)
    gaps = detect_skill_gaps(tokens)
    roadmap = build_roadmap(tokens)
    return summary, gaps, roadmap


