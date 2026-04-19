import { useState } from 'react'
import { useAgents } from '../hooks/useAgents'
import AgentRow from '../components/agent/AgentRow'
import { GlassCard } from '../components/ui/GlassCard'
import type { Agent } from '../types'

function isToday(iso: string | null): boolean {
  if (!iso) return false
  const d = new Date(iso)
  const now = new Date()
  return d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate()
}

function formatAvgDuration(agents: Agent[]): string {
  const completed = agents.filter(a => a.started_at && a.ended_at)
  if (completed.length === 0) return '—'
  const total = completed.reduce((sum, a) => {
    return sum + (new Date(a.ended_at!).getTime() - new Date(a.started_at!).getTime())
  }, 0)
  const avgMs = total / completed.length
  const secs = Math.floor(avgMs / 1000)
  if (secs < 60) return `${secs}s`
  return `${Math.floor(secs / 60)}m ${secs % 60}s`
}

export function LiveMonitorPage() {
  const { data, error } = useAgents(1000)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const agents = data?.agents || []
  const sorted = [...agents].sort((a, b) => {
    if (a.status === 'running' && b.status !== 'running') return -1
    if (a.status !== 'running' && b.status === 'running') return 1
    const aTime = a.ended_at || a.started_at || ''
    const bTime = b.ended_at || b.started_at || ''
    return new Date(bTime).getTime() - new Date(aTime).getTime()
  })

  const runningCount = agents.filter(a => a.status === 'running').length
  const completedToday = agents.filter(a => a.status === 'completed' && isToday(a.started_at)).length

  return (
    <div className="max-w-5xl">
      <div className="flex items-center gap-4 mb-6">
        <h1 className="text-2xl text-h1 title-gradient">Live Monitor</h1>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <GlassCard className="p-4 text-center">
          <span className="eyebrow block mb-1">Running</span>
          <span className="text-3xl font-bold text-green-400">{runningCount}</span>
        </GlassCard>
        <GlassCard className="p-4 text-center">
          <span className="eyebrow block mb-1">Completed Today</span>
          <span className="text-3xl font-bold text-text-high">{completedToday}</span>
        </GlassCard>
        <GlassCard className="p-4 text-center">
          <span className="eyebrow block mb-1">Avg Duration</span>
          <span className="text-3xl font-bold text-text-high">{formatAvgDuration(agents)}</span>
        </GlassCard>
      </div>

      {error && (
        <GlassCard className="p-6 text-center">
          <p className="text-red-400 text-sm">Connection error - is the server running?</p>
        </GlassCard>
      )}

      {!data && !error && (
        <GlassCard className="p-12 text-center">
          <p className="text-text-subtle text-sm">Loading...</p>
        </GlassCard>
      )}

      {data && sorted.length === 0 && (
        <GlassCard className="p-12 text-center">
          <p className="text-text-muted text-lg">No agents running</p>
          <p className="text-text-subtle text-sm mt-2">Agents will appear here when spawned</p>
        </GlassCard>
      )}

      {data && sorted.length > 0 && (
        <div className="glass overflow-hidden">
          {sorted.map((agent, i) => (
            <div key={agent.id}>
              {i > 0 && <div className="border-b border-[rgba(140,170,255,0.08)]" />}
              <AgentRow
                agent={agent}
                expanded={expandedId === agent.id}
                onToggle={() => setExpandedId(expandedId === agent.id ? null : agent.id)}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
