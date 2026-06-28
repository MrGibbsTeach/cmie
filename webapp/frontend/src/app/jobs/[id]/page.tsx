'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams } from 'next/navigation'
import { getJob, publishToTpt } from '@/lib/api'
import type { Job } from '@/lib/types'

const STATUS_CONFIG = {
  pending:   { label: 'Pending',    cls: 'bg-slate-700 text-slate-300' },
  running:   { label: 'Running',    cls: 'bg-amber-500/20 text-amber-400' },
  completed: { label: 'Completed',  cls: 'bg-emerald-500/20 text-emerald-400' },
  failed:    { label: 'Failed',     cls: 'bg-red-500/20 text-red-400' },
}

const TYPE_LABEL: Record<string, string> = {
  unit: 'Full unit',
  lesson: 'Lesson',
  assessment: 'Assessment',
}

function logColor(line: string) {
  if (line.includes('[ERROR]')) return 'text-red-400'
  if (line.includes('[WARNING]') || line.includes('[WARN]')) return 'text-amber-400'
  if (line.includes('Stage:')) return 'text-brand-400 font-semibold'
  if (line.includes('complete') || line.includes('done') || line.includes('created')) return 'text-emerald-400'
  return 'text-slate-300'
}

export default function JobPage() {
  const { id } = useParams<{ id: string }>()
  const [job, setJob] = useState<Job | null>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [done, setDone] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [publishError, setPublishError] = useState('')
  const logRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (done) return
    const interval = setInterval(async () => {
      try {
        const j = await getJob(id)
        setJob(j)
        setLogs(j.logs)
        if (j.status === 'completed' || j.status === 'failed') {
          setDone(true)
          clearInterval(interval)
        }
      } catch {
        // backend temporarily unreachable — keep polling
      }
    }, 1000)
    return () => clearInterval(interval)
  }, [id, done])

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [logs])

  if (!job) return (
    <div className="flex items-center justify-center h-64 text-slate-500 text-sm">Loading...</div>
  )

  const sc = STATUS_CONFIG[job.status]

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <a href="/" className="text-slate-500 hover:text-slate-300 text-sm mb-4 inline-block transition-colors">
          ← Dashboard
        </a>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-white leading-snug">{job.title}</h1>
            <p className="text-slate-500 text-sm mt-0.5">{TYPE_LABEL[job.type] ?? job.type}</p>
          </div>
          <span className={`shrink-0 text-xs font-medium px-3 py-1 rounded-full ${sc.cls}`}>
            {sc.label}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      {job.status === 'running' && (
        <div className="mb-6 h-1 bg-slate-800 rounded-full overflow-hidden">
          <div className="h-full bg-brand-500 rounded-full animate-pulse w-3/4" />
        </div>
      )}

      {/* Log terminal */}
      <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden mb-6">
        <div className="flex items-center gap-2 px-4 py-2.5 border-b border-slate-800 bg-slate-900">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
          <div className="w-2.5 h-2.5 rounded-full bg-amber-500/50" />
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/50" />
          <span className="text-xs text-slate-500 ml-2 font-mono">generation log</span>
          {job.status === 'running' && (
            <span className="ml-auto text-xs text-amber-400 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse inline-block" />
              Live
            </span>
          )}
        </div>
        <div
          ref={logRef}
          className="h-80 overflow-y-auto p-4 font-mono text-xs leading-relaxed space-y-0.5"
        >
          {logs.length === 0 && (
            <span className="text-slate-600">Waiting for output...</span>
          )}
          {logs.map((line, i) => (
            <div key={i} className={logColor(line)}>{line}</div>
          ))}
          {job.status === 'running' && (
            <span className="text-slate-600 animate-pulse">▊</span>
          )}
        </div>
      </div>

      {/* Completion actions */}
      {job.status === 'completed' && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-5">
          <p className="text-emerald-400 font-semibold mb-3 text-sm">Generation complete</p>
          <div className="flex flex-wrap gap-3">
            {job.download_zip && (
              <a
                href={`/api/jobs/${job.id}/download`}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-lg text-sm transition-colors"
              >
                ↓ Download package
              </a>
            )}
            {job.type === 'unit' && !job.publish_status && (
              <button
                onClick={async () => {
                  setPublishing(true)
                  setPublishError('')
                  try {
                    await publishToTpt(job.id)
                  } catch (e: unknown) {
                    setPublishError(e instanceof Error ? e.message : 'Unknown error')
                    setPublishing(false)
                  }
                }}
                disabled={publishing}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg text-sm transition-colors"
              >
                {publishing ? 'Starting…' : '↑ Publish to TPT'}
              </button>
            )}
          </div>
          {publishError && (
            <p className="mt-3 text-xs text-red-400">{publishError}</p>
          )}
        </div>
      )}

      {/* Publish status */}
      {job.publish_status && (
        <div className={`rounded-xl border p-5 mt-4 ${
          job.publish_status === 'completed' ? 'border-indigo-500/30 bg-indigo-500/5' :
          job.publish_status === 'failed'    ? 'border-red-500/30 bg-red-500/5' :
                                               'border-amber-500/30 bg-amber-500/5'
        }`}>
          <p className={`font-semibold text-sm mb-1 ${
            job.publish_status === 'completed' ? 'text-indigo-400' :
            job.publish_status === 'failed'    ? 'text-red-400' :
                                                 'text-amber-400'
          }`}>
            {job.publish_status === 'running'   && 'Publishing to TPT — browser is opening…'}
            {job.publish_status === 'completed' && 'Published to TPT'}
            {job.publish_status === 'failed'    && 'TPT publish failed'}
          </p>
          {job.publish_status === 'running' && (
            <p className="text-xs text-slate-400">Check your screen — a browser window is filling in the TPT form. Review and click Publish when ready.</p>
          )}
          {job.publish_url && (
            <a href={job.publish_url} target="_blank" className="text-sm text-indigo-400 hover:underline mt-1 inline-block">
              View on TPT →
            </a>
          )}
          {job.publish_error && (
            <p className="text-xs text-red-300/70 font-mono mt-1">{job.publish_error}</p>
          )}
        </div>
      )}

      {job.status === 'failed' && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-5">
          <p className="text-red-400 font-semibold mb-1 text-sm">Generation failed</p>
          {job.error && <p className="text-xs text-red-300/70 font-mono">{job.error}</p>}
          <a
            href="/builder"
            className="inline-block mt-3 text-sm text-slate-400 hover:text-white transition-colors"
          >
            Try again →
          </a>
        </div>
      )}
    </div>
  )
}
