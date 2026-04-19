import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { GlassCard } from '../components/ui/GlassCard'
import { GlassButton } from '../components/ui/GlassButton'
import { Badge } from '../components/ui/Badge'
import { AgentTimeline } from '../components/agent/AgentTimeline'
import { useAgents } from '../hooks/useAgents'
import type { Agent } from '../types'

function formatDuration(startedAt: string | null, endedAt: string | null): string {
  if (!startedAt) return '—'
  const start = new Date(startedAt).getTime()
  const end = endedAt ? new Date(endedAt).getTime() : Date.now()
  const secs = Math.floor((end - start) / 1000)
  if (secs < 60) return `${secs}s`
  if (secs < 3600) return `${Math.floor(secs / 60)}m ${secs % 60}s`
  return `${Math.floor(secs / 3600)}h ${Math.floor((secs % 3600) / 60)}m`
}

function getModelShort(model: string): string {
  if (model.includes('opus')) return 'opus'
  if (model.includes('sonnet')) return 'sonnet'
  if (model.includes('haiku')) return 'haiku'
  return model
}

export function AgentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [agent, setAgent] = useState<Agent | null>(null)
  const [loading, setLoading] = useState(true)
  const { data: liveData } = useAgents(agent?.status === 'running' ? 1000 : null)

  useEffect(() => {
    if (!id) return
    const fetchAgent = async () => {
      try {
        const res = await fetch(`/api/history/${id}`)
        if (res.ok) {
          setAgent(await res.json())
        }
      } catch { /* ignore */ }
      setLoading(false)
    }
    fetchAgent()
  }, [id])

  useEffect(() => {
    if (liveData && agent?.status === 'running') {
      const live = liveData.agents.find(a => a.id === id)
      if (live) setAgent(live)
    }
  }, [liveData, agent?.status, id])

  if (loading) {
    return <div className="text-text-subtle">Loading...</div>
  }

  if (!agent) {
    return (
      <div className="max-w-3xl">
        <GlassButton variant="secondary" onClick={() => navigate(-1)} className="mb-4">Back</GlassButton>
        <GlassCard className="p-8 text-center">
          <p className="text-text-muted">Agent not found</p>
        </GlassCard>
      </div>
    )
  }

  return (
    <div className="max-w-4xl">
      <GlassButton variant="secondary" onClick={() => navigate(-1)} className="mb-4">Back</GlassButton>

      <GlassCard className="p-6 mb-6">
        <span className="eyebrow">Agent Details</span>
        <div className="section-divider mt-2" />
        <div className="flex items-center gap-2 flex-wrap mb-4">
          <Badge label={getModelShort(agent.model)} variant="model" />
          <Badge label={agent.status} variant="status" />
          {agent.type !== 'unknown' && <Badge label={agent.type} variant="type" />}
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
          <div>
            <span className="eyebrow block mb-1">Agent ID</span>
            <span className="text-text-high font-mono text-xs">{agent.id}</span>
          </div>
          {agent.session_id && (
            <div>
              <span className="eyebrow block mb-1">Session</span>
              <span className="text-text-high font-mono text-xs">{agent.session_id}</span>
            </div>
          )}
          <div>
            <span className="eyebrow block mb-1">Started</span>
            <span className="text-text-high text-xs">{agent.started_at ? new Date(agent.started_at).toLocaleString() : '—'}</span>
          </div>
          <div>
            <span className="eyebrow block mb-1">Ended</span>
            <span className="text-text-high text-xs">{agent.ended_at ? new Date(agent.ended_at).toLocaleString() : '—'}</span>
          </div>
          <div>
            <span className="eyebrow block mb-1">Duration</span>
            <span className="text-text-high text-xs font-mono">{formatDuration(agent.started_at, agent.ended_at)}</span>
          </div>
        </div>
      </GlassCard>

      <GlassCard className="p-6 mb-6">
        <span className="eyebrow">Prompt</span>
        <div className="section-divider mt-2" />
        <div className="text-sm text-text-base whitespace-pre-wrap break-words max-h-96 overflow-y-auto">
          {agent.prompt || 'No prompt available'}
        </div>
      </GlassCard>

      <div className="mb-4">
        <span className="eyebrow">
          Activity Timeline ({(agent.tool_calls?.length || 0) + (agent.messages?.length || 0)} items)
        </span>
        <div className="section-divider mt-2" />
        <AgentTimeline
          toolCalls={agent.tool_calls || []}
          messages={agent.messages || []}
          startedAt={agent.started_at}
        />
      </div>
    </div>
  )
}
