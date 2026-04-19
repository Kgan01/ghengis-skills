import { Badge } from '../ui/Badge'
import { AgentTimeline } from './AgentTimeline'
import type { Agent } from '../../types'

interface AgentRowProps {
  agent: Agent;
  expanded: boolean;
  onToggle: () => void;
}

function formatElapsed(startedAt: string | null, endedAt: string | null, status: string): string {
  if (!startedAt) return '-'
  const start = new Date(startedAt).getTime()
  const end = (status === 'running' || !endedAt) ? Date.now() : new Date(endedAt).getTime()
  const secs = Math.floor((end - start) / 1000)
  if (secs < 60) return `0m ${secs}s`
  return `${Math.floor(secs / 60)}m ${secs % 60}s`
}

function StatusDot({ status }: { status: string }) {
  if (status === 'running') {
    return <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse-dot flex-shrink-0" />
  }
  if (status === 'failed') {
    return <span className="w-2 h-2 rounded-full bg-red-400 flex-shrink-0" />
  }
  return <span className="w-2 h-2 rounded-full bg-slate-500 flex-shrink-0" />
}

export default function AgentRow({ agent, expanded, onToggle }: AgentRowProps) {
  const promptPreview = (agent.prompt || '').slice(0, 60)
  const elapsed = formatElapsed(agent.started_at, agent.ended_at, agent.status)
  const toolCount = agent.tool_calls?.length || 0
  const hasActivity = toolCount > 0 || (agent.messages?.length || 0) > 0

  return (
    <div className="border-b border-[rgba(140,170,255,0.08)]">
      <div
        className="flex items-center gap-3 py-3 px-4 cursor-pointer hover:bg-[rgba(200,210,255,0.04)] select-none"
        onClick={onToggle}
      >
        <StatusDot status={agent.status} />

        <Badge variant="status" label={(agent as any).subagent_type || agent.type || 'unknown'} />
        <Badge variant="status" label={agent.model || 'unknown'} />

        <span className="flex-1 text-sm text-slate-300 truncate font-mono text-[0.82rem]">
          {promptPreview || '(no prompt)'}
        </span>

        <span className="text-xs text-slate-500 font-mono whitespace-nowrap">{elapsed}</span>
        <span className="text-xs text-slate-500 whitespace-nowrap">{toolCount} tools</span>

        <svg
          className="w-4 h-4 text-slate-500 flex-shrink-0 transition-transform duration-200"
          style={{ transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)' }}
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M6 3l5 5-5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>

      {expanded && (
        <div className="border-t border-[rgba(140,170,255,0.08)]">
          <div className="max-h-[400px] overflow-y-auto p-4">
            {hasActivity ? (
              <AgentTimeline
                toolCalls={agent.tool_calls || []}
                messages={agent.messages || []}
                startedAt={agent.started_at}
              />
            ) : (
              <p className="text-sm text-slate-500">No activity recorded</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
