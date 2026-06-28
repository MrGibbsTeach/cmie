import type { AssessmentRequest, Job, LessonRequest, UnitRequest } from './types'

const BASE = '/api'

export async function getJobs(): Promise<Job[]> {
  const res = await fetch(`${BASE}/jobs`)
  if (!res.ok) throw new Error('Failed to fetch jobs')
  return res.json()
}

export async function getJob(id: string): Promise<Job> {
  const res = await fetch(`${BASE}/jobs/${id}`)
  if (!res.ok) throw new Error('Failed to fetch job')
  return res.json()
}

export async function generateUnit(req: UnitRequest): Promise<{ job_id: string }> {
  const res = await fetch(`${BASE}/generate/unit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to start unit generation')
  }
  return res.json()
}

export async function generateLesson(req: LessonRequest): Promise<{ job_id: string }> {
  const res = await fetch(`${BASE}/generate/lesson`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to start lesson generation')
  }
  return res.json()
}

export async function generateAssessment(req: AssessmentRequest): Promise<{ job_id: string }> {
  const res = await fetch(`${BASE}/generate/assessment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to start assessment generation')
  }
  return res.json()
}

export async function publishToTpt(jobId: string): Promise<{ publish_status: string }> {
  const res = await fetch(`${BASE}/jobs/${jobId}/publish/tpt`, { method: 'POST' })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to start TPT publish')
  }
  return res.json()
}

export function streamJobLogs(
  jobId: string,
  onLog: (line: string) => void,
  onDone: (status: string, error?: string) => void,
): () => void {
  const source = new EventSource(`${BASE}/jobs/${jobId}/stream`)

  source.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data)
      if (data.done) {
        onDone(data.status, data.error)
        source.close()
      } else if (data.log) {
        onLog(data.log)
      }
    } catch {
      // ignore parse errors
    }
  }

  source.onerror = () => {
    onDone('failed', 'Connection lost')
    source.close()
  }

  return () => source.close()
}
