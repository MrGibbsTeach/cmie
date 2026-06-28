'use client'

import { useEffect, useState } from 'react'
import { getJobs } from '@/lib/api'
import type { Job } from '@/lib/types'

const STATUS_CONFIG = {
  pending:   { label: 'Pending',   cls: 'bg-slate-700 text-slate-300' },
  running:   { label: 'Running',   cls: 'bg-amber-500/20 text-amber-400' },
  completed: { label: 'Done',      cls: 'bg-emerald-500/20 text-emerald-400' },
  failed:    { label: 'Failed',    cls: 'bg-red-500/20 text-red-400' },
}

const TYPE_ICON: Record<string, string> = {
  unit: '📦',
  lesson: '📄',
  assessment: '📝',
}

function timeAgo(iso: string) {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

export default function DashboardPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        setJobs(await getJobs())
      } catch {
        // backend not yet running
      } finally {
        setLoading(false)
      }
    }
    load()
    const interval = setInterval(load, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Dashboard</h1>
        <p className="text-slate-400 text-sm">All generation jobs</p>
      </div>

      {loading && (
        <div className="text-slate-500 text-sm">Loading...</div>
      )}

      {!loading && jobs.length === 0 && (
        <div className="text-center py-20 border border-dashed border-slate-800 rounded-xl">
          <p className="text-slate-400 mb-4">No generations yet.</p>
          <a
            href="/builder"
            className="inline-block px-5 py-2.5 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-sm font-medium transition-colors"
          >
            Build your first course
          </a>
        </div>
      )}

      {jobs.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {jobs.map((job) => {
            const sc = STATUS_CONFIG[job.status]
            return (
              <a
                key={job.id}
                href={`/jobs/${job.id}`}
                className="block rounded-xl border border-slate-800 bg-slate-900 p-5 hover:border-slate-600 hover:bg-slate-800/60 transition-all group"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="text-xl">{TYPE_ICON[job.type] ?? '🔧'}</span>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${sc.cls}`}>
                    {sc.label}
                  </span>
                </div>
                <p className="font-semibold text-white text-sm leading-snug mb-1 group-hover:text-brand-400 transition-colors line-clamp-2">
                  {job.title}
                </p>
                <p className="text-xs text-slate-500 capitalize mb-3">{job.type}</p>
                <div className="flex items-center justify-between text-xs text-slate-600">
                  <span>{timeAgo(job.created_at)}</span>
                  {job.status === 'running' && (
                    <span className="flex items-center gap-1 text-amber-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                      Live
                    </span>
                  )}
                  {job.status === 'completed' && job.download_zip && (
                    <span className="text-emerald-500">↓ Ready</span>
                  )}
                </div>
              </a>
            )
          })}
        </div>
      )}
    </div>
  )
}
