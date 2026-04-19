import { useNavigate } from 'react-router-dom'
import { GlassCard } from '../ui/GlassCard'
import { Badge } from '../ui/Badge'
import type { Agent } from '../../types'

function formatDuration(startedAt: string | null, endedAt: string | null): string {
  if (!startedAt) return '-'
  const start = new Date(startedAt).getTime()
  const end = endedAt ? new Date(endedAt).getTime() : Date.now()
  const secs = Math.floor((end - start) / 1000)
  if (secs < 60) return `${secs}s`
  return `${Math.floor(secs / 60)}m ${secs % 60}s`
}

function getModelShort(model: string): string {
  if (model.includes('opus')) return 'opus'
  if (model.includes('sonnet')) return 'sonnet'
  if (model.includes('haiku')) return 'haiku'
  return model.split('-').pop() || model
}

export function AgentCard({ agent }: { agent: Agent }) {
  const navigate = useNavigate()
  const modelShort = getModelShort(agent.model)
  const duration = formatDuration(agent.started_at, agent.ended_at)
  const promptPreview = (agent.prompt || 'No prompt').slice(0, 200)
  const toolCalls = agent.tool_calls || []
  const recentTools = toolCalls.slice(-3)

  return (
    <GlassCard hover onClick={() => navigate(`/agent/${agent.id}`)} className="p-4">
      <div className="flex items-center gap-2 mb-3 flex-wrap">
        <Badge label={modelShort} variant="model" />
        <Badge label={agent.status} variant="status" />
        {agent.type && agent.type !== 'unknown' && (
          <Badge label={agent.type} variant="type" />
        )}
        <span className="text-xs text-text-subtle ml-auto">{duration}</span>
      </div>

      {agent.status === 'running' && (
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse-dot" />
          <span className="text-xs text-amber-400 font-medium">Running</span>
        </div>
      )}

      <p className="text-sm text-text-base leading-relaxed mb-3 line-clamp-3">
        {promptPreview}{agent.prompt && agent.prompt.length > 200 ? '...' : ''}
      </p>

      {recentTools.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {recentTools.map((t, i) => (
            <Badge key={i} label={t.name} variant="tool" />
          ))}
          {toolCalls.length > 3 && (
            <span className="text-xs text-text-subtle self-center">+{toolCalls.length - 3} more</span>
          )}
        </div>
      )}
    </GlassCard>
  )
}
