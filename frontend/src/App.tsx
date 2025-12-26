import React, { useState } from 'react'
import UploadResume from '@/components/UploadResume'
import AnalysisResults from '@/components/AnalysisResults'
import JobList from '@/components/JobList'
import { api } from '@/services/api'
import type { Analysis, Job } from '@/types'

export default function App() {
  const [analysis, setAnalysis] = useState<Analysis | undefined>()
  const [loading, setLoading] = useState(false)
  const [keywords, setKeywords] = useState('')
  const [loadingJobs, setLoadingJobs] = useState(false)
  const [linkedinJobs, setLinkedinJobs] = useState<Job[]>([])
  const [naukriJobs, setNaukriJobs] = useState<Job[]>([])

  const onUpload = async (file: File) => {
    setLoading(true)
    try {
      const result = await api.analyzeResume(file)
      setAnalysis(result)
    } catch (e) {
      console.error(e)
      alert('Failed to analyze resume')
    } finally {
      setLoading(false)
    }
  }

  const onGetJobs = async () => {
    if (!analysis?.summary) return
    setLoadingJobs(true)
    try {
      const kw = await api.getKeywords(analysis.summary)
      const cleaned = kw.replace(/\n/g, '').trim()
      setKeywords(cleaned)
      const { linkedinJobs, naukriJobs } = await api.getJobs(cleaned)
      setLinkedinJobs(linkedinJobs)
      setNaukriJobs(naukriJobs)
    } catch (e) {
      console.error(e)
      alert('Failed to fetch jobs')
    } finally {
      setLoadingJobs(false)
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>📄 AI Job Recommender</h1>
      </div>
      <p className="helper">Upload your resume and get job recommendations based on your skills and experience from LinkedIn and Naukri.</p>

      <UploadResume onUpload={onUpload} loading={loading} />
      <div style={{ height: 12 }} />
      <AnalysisResults analysis={analysis} loading={loading} />

      <div className="card">
        <h3 className="section-title">Recommendations</h3>
        <button className="button" disabled={!analysis || loadingJobs} onClick={onGetJobs}>
          {loadingJobs ? 'Fetching…' : '🔎 Get Job Recommendations'}
        </button>
        {keywords && (
          <p className="helper">Extracted Job Keywords: {keywords}</p>
        )}
      </div>

      <div className="row" style={{ marginTop: 16 }}>
        <JobList title="💼 Top LinkedIn Jobs" jobs={linkedinJobs} />
        <JobList title="💼 Top Naukri Jobs (India)" jobs={naukriJobs} />
      </div>
    </div>
  )
}
