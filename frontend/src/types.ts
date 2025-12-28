export type Analysis = {
  summary: string
  gaps: string
  roadmap: string
}

export type Job = {
  title: string
  companyName: string
  location?: string
  url?: string // Primary job link
  source?: string // e.g., RSS feed name
}
