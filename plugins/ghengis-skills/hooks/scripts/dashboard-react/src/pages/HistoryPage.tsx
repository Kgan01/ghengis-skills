import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useHistory } from '../hooks/useHistory'
import { Badge } from '../components/ui/Badge'
import { GlassInput } from '../components/ui/GlassInput'
import { GlassSelect } from '../components/ui/GlassSelect'
import { GlassButton } from '../components/ui/GlassButton'
import type { Agent } from '../types'

function formatTime(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) +
    ', ' +
    d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
}

function formatDuration(started: string | null, ended: string | null): string {
  if (!started || !ended) return '—'
  const ms = new Date(ended).getTime() - new Date(started).getTime()
  if (ms < 0) return '—'
  const totalSeconds = Math.floor(ms / 1000)
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  if (m === 0) return `${s}s`
  return `${m}m ${s}s`
}

function TableRow({ agent }: { agent: Agent }) {
  const navigate = useNavigate()
  const toolCount = agent.tool_call_count ?? agent.tool_calls?.length ?? 0

  return (
    <div
      className="grid items-center px-4 py-3 border-b border-[rgba(140,170,255,0.08)] cursor-pointer hover:bg-[rgba(200,210,255,0.04)] transition-colors"
      style={{ gridTemplateColumns: '140px 110px 90px 80px 1fr 60px 90px' }}
      onClick={() => navigate(`/agent/${agent.id}`)}
    >
      <span className="text-text-muted text-xs tabular-nums">{formatTime(agent.started_at)}</span>
      <span><Badge label={agent.type} variant="type" /></span>
      <span><Badge label={agent.model} variant="model" /></span>
      <span className="text-text-muted text-xs tabular-nums">{formatDuration(agent.started_at, agent.ended_at)}</span>
      <span className="truncate font-mono text-[0.82rem] text-text-base pr-4">{agent.prompt}</span>
      <span className="text-text-muted text-xs text-center">{toolCount > 0 ? toolCount : '—'}</span>
      <span><Badge label={agent.status} variant="status" /></span>
    </div>
  )
}

export function HistoryPage() {
  const [search, setSearch] = useState('')
  const [modelFilter, setModelFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [offset, setOffset] = useState(0)

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300)
    return () => clearTimeout(t)
  }, [search])

  useEffect(() => { setOffset(0) }, [debouncedSearch, modelFilter, typeFilter, dateFrom, dateTo])

  const filters = useMemo(() => ({
    q: debouncedSearch || undefined,
    model: modelFilter || undefined,
    type: typeFilter || undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
    limit: 50,
    offset,
  }), [debouncedSearch, modelFilter, typeFilter, dateFrom, dateTo, offset])

  const { data, loading } = useHistory(filters)

  return (
    <div className="max-w-6xl">
      <div className="flex items-center gap-4 mb-6">
        <h1 className="text-2xl text-h1 title-gradient">Agent History</h1>
        {data && (
          <span className="bg-white/5 border border-white/10 px-2.5 py-0.5 rounded-full text-xs font-medium text-text-muted">
            {data.total} agents
          </span>
        )}
      </div>

      <div className="flex flex-wrap gap-3 mb-6">
        <div className="flex-1 min-w-[200px]">
          <GlassInput
            placeholder="Search prompts..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="w-36">
          <GlassSelect value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
            <option value="">All types</option>
            <option value="general-purpose">General Purpose</option>
            <option value="Explore">Explore</option>
            <option value="Plan">Plan</option>
            <option value="frontend-design">Frontend Design</option>
          </GlassSelect>
        </div>
        <div className="w-36">
          <GlassSelect value={modelFilter} onChange={e => setModelFilter(e.target.value)}>
            <option value="">All models</option>
            <option value="opus">Opus</option>
            <option value="sonnet">Sonnet</option>
            <option value="haiku">Haiku</option>
          </GlassSelect>
        </div>
        <div className="w-40">
          <GlassInput
            type="date"
            value={dateFrom}
            onChange={e => setDateFrom(e.target.value)}
          />
        </div>
        <div className="w-40">
          <GlassInput
            type="date"
            value={dateTo}
            onChange={e => setDateTo(e.target.value)}
          />
        </div>
      </div>

      <div className="glass overflow-hidden">
        <div
          className="grid px-4 py-2.5 border-b border-[rgba(140,170,255,0.12)]"
          style={{ gridTemplateColumns: '140px 110px 90px 80px 1fr 60px 90px' }}
        >
          <span className="eyebrow">Time</span>
          <span className="eyebrow">Type</span>
          <span className="eyebrow">Model</span>
          <span className="eyebrow">Duration</span>
          <span className="eyebrow">Prompt</span>
          <span className="eyebrow text-center">Tools</span>
          <span className="eyebrow">Status</span>
        </div>

        {loading && !data && (
          <div className="py-16 text-center text-text-subtle text-sm">Loading...</div>
        )}

        {data && data.agents.length === 0 && (
          <div className="py-16 text-center text-text-subtle text-sm">No history found</div>
        )}

        {data && data.agents.map(agent => (
          <TableRow key={agent.id} agent={agent} />
        ))}
      </div>

      {data && data.total > offset + 50 && (
        <div className="flex justify-center mt-4">
          <GlassButton variant="secondary" onClick={() => setOffset(o => o + 50)}>
            Load more
          </GlassButton>
        </div>
      )}
    </div>
  )
}
