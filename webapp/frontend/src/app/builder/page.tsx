'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { generateUnit, generateLesson, generateAssessment } from '@/lib/api'
import type { Topic } from '@/lib/types'

type TabId = 'unit' | 'lesson' | 'assessment'

const YEAR_LEVELS = ['Year 7', 'Year 8', 'Year 9', 'Year 10', 'Year 11', 'Year 12']
const SUBJECTS = ['Digital Technologies', 'Computer Science', 'STEM', 'ICT', 'Mathematics', 'Science']

function slugify(s: string) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '')
}

function Input({ label, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-medium text-slate-300">{label}</label>
      <input
        {...props}
        className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
      />
    </div>
  )
}

function Select({ label, options, ...props }: React.SelectHTMLAttributes<HTMLSelectElement> & { label: string; options: string[] }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-medium text-slate-300">{label}</label>
      <select
        {...props}
        className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
      >
        <option value="">Select...</option>
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  )
}

// ------------------------------------------------------------------
// Unit form
// ------------------------------------------------------------------
function UnitForm() {
  const router = useRouter()
  const [title, setTitle] = useState('')
  const [yearLevel, setYearLevel] = useState('')
  const [subject, setSubject] = useState('')
  const [version, setVersion] = useState('v001')
  const [topics, setTopics] = useState<Topic[]>([{ title: '', video_url: '' }])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const addTopic = () => setTopics([...topics, { title: '', video_url: '' }])
  const removeTopic = (i: number) => setTopics(topics.filter((_, idx) => idx !== i))
  const updateTopic = (i: number, field: keyof Topic, val: string) => {
    setTopics(topics.map((t, idx) => idx === i ? { ...t, [field]: val } : t))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title || !yearLevel || !subject) { setError('Fill in all required fields.'); return }
    if (topics.some(t => !t.title.trim())) { setError('All lessons need a title.'); return }
    setError('')
    setSubmitting(true)
    try {
      const { job_id } = await generateUnit({
        unit_id: slugify(title),
        title,
        year_level: yearLevel,
        subject,
        version,
        topics: topics.map(t => ({ title: t.title.trim(), video_url: t.video_url || undefined })),
      })
      router.push(`/jobs/${job_id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="grid sm:grid-cols-2 gap-4">
        <Input label="Unit title *" value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. AI and Data Ethics" />
        <Input label="Version" value={version} onChange={e => setVersion(e.target.value)} placeholder="v001" />
        <Select label="Year level *" value={yearLevel} onChange={e => setYearLevel(e.target.value)} options={YEAR_LEVELS} />
        <Select label="Subject *" value={subject} onChange={e => setSubject(e.target.value)} options={SUBJECTS} />
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <label className="text-sm font-medium text-slate-300">Lessons</label>
          <button type="button" onClick={addTopic} className="text-xs text-brand-400 hover:text-brand-300 font-medium transition-colors">
            + Add lesson
          </button>
        </div>
        <div className="space-y-2">
          {topics.map((topic, i) => (
            <div key={i} className="flex gap-2 items-start">
              <div className="flex-1 grid sm:grid-cols-2 gap-2">
                <input
                  value={topic.title}
                  onChange={e => updateTopic(i, 'title', e.target.value)}
                  placeholder={`Lesson ${i + 1} title`}
                  className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 transition"
                />
                <input
                  value={topic.video_url || ''}
                  onChange={e => updateTopic(i, 'video_url', e.target.value)}
                  placeholder="Video URL (optional)"
                  className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 transition"
                />
              </div>
              {topics.length > 1 && (
                <button type="button" onClick={() => removeTopic(i)} className="text-slate-600 hover:text-red-400 text-lg mt-1.5 transition-colors">×</button>
              )}
            </div>
          ))}
        </div>
      </div>

      {error && <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">{error}</p>}
      <button
        type="submit"
        disabled={submitting}
        className="w-full py-3 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg text-sm transition-colors"
      >
        {submitting ? 'Starting generation...' : 'Generate full unit'}
      </button>
    </form>
  )
}

// ------------------------------------------------------------------
// Lesson form
// ------------------------------------------------------------------
function LessonForm() {
  const router = useRouter()
  const [unitTitle, setUnitTitle] = useState('')
  const [yearLevel, setYearLevel] = useState('')
  const [topicTitle, setTopicTitle] = useState('')
  const [lessonNumber, setLessonNumber] = useState('1')
  const [videoUrl, setVideoUrl] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!unitTitle || !yearLevel || !topicTitle) { setError('Fill in all required fields.'); return }
    setError('')
    setSubmitting(true)
    try {
      const { job_id } = await generateLesson({
        unit_title: unitTitle,
        year_level: yearLevel,
        topic_title: topicTitle,
        lesson_number: parseInt(lessonNumber) || 1,
        video_url: videoUrl || undefined,
      })
      router.push(`/jobs/${job_id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid sm:grid-cols-2 gap-4">
        <Input label="Unit / course title *" value={unitTitle} onChange={e => setUnitTitle(e.target.value)} placeholder="e.g. AI and Data Ethics" />
        <Select label="Year level *" value={yearLevel} onChange={e => setYearLevel(e.target.value)} options={YEAR_LEVELS} />
        <Input label="Lesson topic *" value={topicTitle} onChange={e => setTopicTitle(e.target.value)} placeholder="e.g. How AI learns from data" />
        <Input label="Lesson number" type="number" value={lessonNumber} onChange={e => setLessonNumber(e.target.value)} min="1" />
        <div className="sm:col-span-2">
          <Input label="Video URL (optional)" value={videoUrl} onChange={e => setVideoUrl(e.target.value)} placeholder="https://..." />
        </div>
      </div>
      {error && <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">{error}</p>}
      <button
        type="submit"
        disabled={submitting}
        className="w-full py-3 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg text-sm transition-colors"
      >
        {submitting ? 'Starting generation...' : 'Generate lesson'}
      </button>
    </form>
  )
}

// ------------------------------------------------------------------
// Assessment form
// ------------------------------------------------------------------
function AssessmentForm() {
  const router = useRouter()
  const [title, setTitle] = useState('')
  const [yearLevel, setYearLevel] = useState('')
  const [subject, setSubject] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title || !yearLevel || !subject) { setError('Fill in all required fields.'); return }
    setError('')
    setSubmitting(true)
    try {
      const { job_id } = await generateAssessment({
        unit_id: slugify(title),
        title,
        year_level: yearLevel,
        subject,
      })
      router.push(`/jobs/${job_id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid sm:grid-cols-2 gap-4">
        <Input label="Unit / course title *" value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. AI and Data Ethics" />
        <Select label="Year level *" value={yearLevel} onChange={e => setYearLevel(e.target.value)} options={YEAR_LEVELS} />
        <Select label="Subject *" value={subject} onChange={e => setSubject(e.target.value)} options={SUBJECTS} />
      </div>
      {error && <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">{error}</p>}
      <button
        type="submit"
        disabled={submitting}
        className="w-full py-3 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg text-sm transition-colors"
      >
        {submitting ? 'Starting generation...' : 'Generate assessment'}
      </button>
    </form>
  )
}

// ------------------------------------------------------------------
// Page
// ------------------------------------------------------------------
const TABS: { id: TabId; label: string; icon: string; description: string }[] = [
  { id: 'unit',       label: 'Full unit',   icon: '📦', description: 'Lessons + workbook + assessment + marketing' },
  { id: 'lesson',     label: 'Lesson',      icon: '📄', description: 'Single lesson with slides and workbook page' },
  { id: 'assessment', label: 'Assessment',  icon: '📝', description: 'Task, rubric, and marking guide' },
]

export default function BuilderPage() {
  const [tab, setTab] = useState<TabId>('unit')

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">New generation</h1>
        <p className="text-slate-400 text-sm">Choose what you want to build</p>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-8">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`rounded-xl border p-4 text-left transition-all ${
              tab === t.id
                ? 'border-brand-500 bg-brand-600/10 ring-1 ring-brand-500/50'
                : 'border-slate-800 bg-slate-900 hover:border-slate-600'
            }`}
          >
            <span className="text-2xl mb-2 block">{t.icon}</span>
            <p className="text-sm font-semibold text-white mb-1">{t.label}</p>
            <p className="text-xs text-slate-500 leading-snug">{t.description}</p>
          </button>
        ))}
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        {tab === 'unit' && <UnitForm />}
        {tab === 'lesson' && <LessonForm />}
        {tab === 'assessment' && <AssessmentForm />}
      </div>
    </div>
  )
}
