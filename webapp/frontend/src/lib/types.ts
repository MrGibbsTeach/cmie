export type JobStatus = 'pending' | 'running' | 'completed' | 'failed'
export type JobType = 'unit' | 'lesson' | 'assessment'
export type PublishStatus = 'running' | 'completed' | 'failed'

export interface Job {
  id: string
  type: JobType
  status: JobStatus
  title: string
  config: Record<string, unknown>
  logs: string[]
  created_at: string
  completed_at: string | null
  output_path: string | null
  download_zip: string | null
  error: string | null
  publish_status: PublishStatus | null
  publish_url: string | null
  publish_error: string | null
  thumbnail_path: string | null
}

export interface Topic {
  title: string
  video_url?: string
}

export interface UnitRequest {
  unit_id: string
  title: string
  year_level: string
  subject: string
  version: string
  topics: Topic[]
}

export interface LessonRequest {
  unit_title: string
  year_level: string
  topic_title: string
  lesson_number: number
  video_url?: string
}

export interface AssessmentRequest {
  unit_id: string
  title: string
  year_level: string
  subject: string
}
