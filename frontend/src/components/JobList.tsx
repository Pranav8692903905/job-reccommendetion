import React from 'react'
import type { Job } from '@/types'

interface Props {
  title: string
  jobs: Job[]
}

export default function JobList({ title, jobs }: Props) {
  return (
    <div className="card">
      <h3 className="section-title">{title}</h3>
      {jobs.length === 0 && <div className="helper">No jobs found yet.</div>}
      <div className="list">
        {jobs.map((job, idx) => (
          <div className="job" key={idx}>
            <h4>{job.title} <span className="helper">@ {job.companyName}</span></h4>
            {job.location && <div className="helper">📍 {job.location}</div>}
            {job.source && <div className="pill">{job.source}</div>}
            {job.url && (
              <div><a href={job.url} target="_blank" rel="noreferrer">View Role</a></div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
