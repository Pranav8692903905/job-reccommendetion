import axios from 'axios'
import type { Analysis, Job } from '@/types'

const useMock = (import.meta.env.VITE_USE_MOCK ?? 'true') === 'true'

async function sleep(ms: number) {
  return new Promise((res) => setTimeout(res, ms))
}

// ---- Real API layer (expects a Python server at localhost:8000) ----
async function analyzeResumeReal(file: File): Promise<Analysis> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await axios.post('/api/analyze/resume', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

async function getKeywordsReal(summary: string): Promise<string> {
  const { data } = await axios.post('/api/keywords', { summary })
  return data?.keywords ?? ''
}

async function getJobsReal(keywords: string): Promise<{ linkedinJobs: Job[]; naukriJobs: Job[] }> {
  const { data } = await axios.get('/api/jobs', { params: { keywords } })
  return data
}

// ---- Mock API layer (runs without backend) ----
async function analyzeResumeMock(file: File): Promise<Analysis> {
  await sleep(700)
  return {
    summary:
      "Experienced Data Scientist with 5+ years in NLP and ML, proficient in Python, SQL, and cloud services. Delivered end-to-end ML systems and LLM-backed apps.",
    gaps:
      "Missing advanced MLOps exposure (Kubeflow), limited production-scale vector DB experience, and formal certifications in Azure or AWS ML.",
    roadmap:
      "1) Learn orchestration (Prefect/Kubeflow). 2) Earn AWS ML Specialty. 3) Build a retrieval-augmented generation app with embeddings and evaluation."
  }
}

async function getKeywordsMock(summary: string): Promise<string> {
  await sleep(400)
  return 'Data Scientist, NLP Engineer, LLM Engineer, Machine Learning Engineer'
}

async function getJobsMock(keywords: string): Promise<{ linkedinJobs: Job[]; naukriJobs: Job[] }> {
  await sleep(600)
  return {
    linkedinJobs: [
      { title: 'Machine Learning Engineer', companyName: 'TechCorp', location: 'Remote', link: 'https://www.linkedin.com/jobs' },
      { title: 'NLP Engineer', companyName: 'LinguaAI', location: 'Bengaluru, IN', link: 'https://www.linkedin.com/jobs' }
    ],
    naukriJobs: [
      { title: 'Data Scientist', companyName: 'AnalyticsHub', location: 'Pune, IN', url: 'https://www.naukri.com' },
      { title: 'LLM Engineer', companyName: 'ModelWorks', location: 'Hyderabad, IN', url: 'https://www.naukri.com' }
    ]
  }
}

export const api = {
  analyzeResume: (file: File) => (useMock ? analyzeResumeMock(file) : analyzeResumeReal(file)),
  getKeywords: (summary: string) => (useMock ? getKeywordsMock(summary) : getKeywordsReal(summary)),
  getJobs: (keywords: string) => (useMock ? getJobsMock(keywords) : getJobsReal(keywords)),
}
