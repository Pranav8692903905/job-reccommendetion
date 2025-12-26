import React from 'react'
import type { Analysis } from '@/types'

interface Props {
  analysis?: Analysis
  loading: boolean
}

export default function AnalysisResults({ analysis, loading }: Props) {
  return (
    <div className="card">
      <h3 className="section-title">Analysis</h3>
      {loading && <div className="spinner">Analyzing resume…</div>}
      {!loading && !analysis && <div className="helper">Upload a resume to see results.</div>}
      {!loading && analysis && (
        <div className="row">
          <div className="card">
            <h4 className="section-title">📑 Resume Summary</h4>
            <div>{analysis.summary}</div>
          </div>
          <div className="card">
            <h4 className="section-title">🛠️ Skill Gaps & Missing Areas</h4>
            <div>{analysis.gaps}</div>
          </div>
          <div className="card" style={{ gridColumn: '1 / -1' }}>
            <h4 className="section-title">🚀 Future Roadmap & Preparation Strategy</h4>
            <div>{analysis.roadmap}</div>
          </div>
        </div>
      )}
    </div>
  )
}
