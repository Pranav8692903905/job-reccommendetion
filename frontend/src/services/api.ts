import axios from 'axios'
import type { Analysis, Job } from '@/types'

// Real API layer (expects a Python server at localhost:8000)
async function analyzeResume(file: File): Promise<Analysis> {
  const form = new FormData()
  form.append('file', file)
  try {
    const response = await axios.post('/api/analyze/resume', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    console.log('Backend response:', response.data)
    
    // Validate response structure
    const data = response.data
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid response format from server')
    }
    if (!data.summary || !data.gaps || !data.roadmap) {
      console.error('Missing fields in response:', data)
      throw new Error('Incomplete analysis data from server')
    }
    
    return data as Analysis
  } catch (err) {
    console.error('API error details:', err)
    if (axios.isAxiosError(err)) {
      if (err.response) {
        console.error('Response status:', err.response.status)
        console.error('Response data:', err.response.data)
        throw new Error(`Server error (${err.response.status}): ${JSON.stringify(err.response.data)}`)
      } else if (err.request) {
        console.error('No response received:', err.request)
        throw new Error('No response from server. Is the backend running?')
      }
    }
    throw err
  }
}

async function getKeywords(summary: string): Promise<string> {
  const { data } = await axios.post('/api/keywords', { summary })
  return data?.keywords ?? ''
}

async function getJobs(keywords: string): Promise<{ jobs: Job[] }> {
  const { data } = await axios.get('/api/jobs', { params: { keywords } })
  return data
}

export const api = {
  analyzeResume,
  getKeywords,
  getJobs,
}
