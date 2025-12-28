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
  const [jobs, setJobs] = useState<Job[]>([])

  const onUpload = async (file: File) => {
    setLoading(true)
    try {
      const result = await api.analyzeResume(file)
      console.log('Analysis result:', result)
      setAnalysis(result)
    } catch (e) {
      console.error('Analysis error:', e)
      const errMsg = e instanceof Error ? e.message : String(e)
      alert(`Failed to analyze resume: ${errMsg}`)
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
      const { jobs } = await api.getJobs(cleaned)
      setJobs(jobs)
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
        <div>
          <p className="eyebrow">AI + RSS MATCHER</p>
          <h1>📄 Smart Job Recommender</h1>
          <p className="helper">Upload your resume, extract the strongest keywords, and browse a clean feed of curated roles aggregated from RSS-powered job sources.</p>
        </div>
        <div className="badge">Live</div>
      </div>

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
        <JobList title="💼 Fresh Roles from RSS Feeds" jobs={jobs} />
      </div>
    </div>
  )
}
