import { useState, useMemo } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useHistory } from '../hooks/useHistory'
import { useProjects } from '../hooks/useProjects'
import { Badge } from '../components/ui/Badge'
import { GlassSelect } from '../components/ui/GlassSelect'
import { Skeleton } from '../components/ui/Skeleton'
import type { Agent, Project } from '../types'

type TimeRange = '24h' | '7d' | '30d' | 'all'

const MAX_PER_GROUP = 20

function getDateFrom(range: TimeRange): string | undefined {
  if (range === 'all') return undefined
  const now = new Date()
  if (range === '24h') now.setHours(now.getHours() - 24)
  else if (range === '7d') now.setDate(now.getDate() - 7)
  else if (range === '30d') now.setDate(now.getDate() - 30)
  return now.toISOString()
}

function formatTimestamp(iso: string | null): string {
  if (!iso) return '--'
  const d = new Date(iso)
  return (
    d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) +
    ' ' +
    d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
  )
}

function formatRelative(iso: string | null): string {
  if (!iso) return '--'
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const day = Math.floor(h / 24)
  return `${day}d ago`
}

interface AgentRowProps {
  agent: Agent
}

function AgentRow({ agent }: AgentRowProps) {
  const navigate = useNavigate()
  const timestamp = agent.started_at ?? agent.last_activity

  return (
    <div
      className="grid items-center gap-3 px-4 py-2.5 border-b border-[rgba(140,170,255,0.06)] cursor-pointer hover:bg-[rgba(200,210,255,0.04)] transition-colors"
      style={{ gridTemplateColumns: '130px 80px 80px 90px 110px 1fr' }}
      onClick={() => navigate(`/agent/${agent.id}`)}
    >
      <span className="text-text-subtle text-xs tabular-nums">{formatTimestamp(timestamp)}</span>
      <span><Badge label={agent.status} variant="status" /></span>
      <span><Badge label={agent.type} variant="type" /></span>
      <span><Badge label={agent.model} variant="model" /></span>
      {agent.git_branch ? (
        <span>
          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-mono bg-[rgba(140,170,255,0.08)] border border-[rgba(140,170,255,0.15)] text-text-muted truncate max-w-[100px]">
            {agent.git_branch}
          </span>
        </span>
      ) : (
        <span className="text-text-subtle text-xs">--</span>
      )}
      <span className="truncate font-mono text-[0.8rem] text-text-muted pr-2">
        {agent.prompt}
      </span>
    </div>
  )
}

interface ProjectGroupProps {
  project: Project
  agents: Agent[]
  defaultExpanded?: boolean
}

function ProjectGroup({ project, agents, defaultExpanded = true }: ProjectGroupProps) {
  const [expanded, setExpanded] = useState(defaultExpanded)

  const latestAgent = agents[0]
  const latestTime = latestAgent?.started_at ?? latestAgent?.last_activity ?? null
  const visibleAgents = agents.slice(0, MAX_PER_GROUP)
  const overflowCount = agents.length - MAX_PER_GROUP

  return (
    <div className="glass mb-3 overflow-hidden">
      {/* Group header */}
      <button
        className="w-full flex items-center gap-3 px-4 py-3 border-b border-[rgba(140,170,255,0.10)] hover:bg-[rgba(200,210,255,0.04)] transition-colors text-left"
        onClick={() => setExpanded(e => !e)}
      >
        <span
          className="inline-block w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: project.color || '#6b7280' }}
        />
        <Link
          to={`/projects/${encodeURIComponent(project.project_name)}`}
          className="text-text-high font-semibold hover:text-primary-400 transition-colors"
          onClick={e => e.stopPropagation()}
        >
          {project.display_name}
        </Link>
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-[rgba(140,170,255,0.10)] border border-[rgba(140,170,255,0.15)] text-text-muted tabular-nums">
          {agents.length}
        </span>
        {latestTime && (
          <span className="text-text-subtle text-xs tabular-nums ml-1">{formatRelative(latestTime)}</span>
        )}
        <span className="ml-auto text-text-subtle text-xs select-none">
          {expanded ? '▲' : '▼'}
        </span>
      </button>

      {/* Agent rows */}
      {expanded && (
        <>
          {/* Column headers */}
          <div
            className="grid gap-3 px-4 py-2 border-b border-[rgba(140,170,255,0.08)] bg-[rgba(200,210,255,0.02)]"
            style={{ gridTemplateColumns: '130px 80px 80px 90px 110px 1fr' }}
          >
            <span className="eyebrow">Time</span>
            <span className="eyebrow">Status</span>
            <span className="eyebrow">Type</span>
            <span className="eyebrow">Model</span>
            <span className="eyebrow">Branch</span>
            <span className="eyebrow">Prompt</span>
          </div>

          {visibleAgents.map(agent => (
            <AgentRow key={agent.id} agent={agent} />
          ))}

          {overflowCount > 0 && (
            <Link
              to={`/projects/${encodeURIComponent(project.project_name)}`}
              className="flex items-center justify-center py-2.5 text-xs text-text-subtle hover:text-text-muted transition-colors border-t border-[rgba(140,170,255,0.06)]"
            >
              +{overflowCount} more agents - view project
            </Link>
          )}
        </>
      )}
    </div>
  )
}

export function ProjectTimelinePage() {
  const [timeRange, setTimeRange] = useState<TimeRange>('7d')

  const dateFrom = useMemo(() => getDateFrom(timeRange), [timeRange])

  const { data: historyData, loading: historyLoading } = useHistory(
    useMemo(
      () => ({ date_from: dateFrom, limit: 500 }),
      [dateFrom]
    )
  )

  const { data: projectsData, loading: projectsLoading } = useProjects()

  const loading = historyLoading || projectsLoading

  // Build a map from project_name -> Project for metadata
  const projectMap = useMemo<Map<string, Project>>(() => {
    const m = new Map<string, Project>()
    if (!projectsData) return m
    for (const p of projectsData.projects) {
      m.set(p.project_name, p)
    }
    return m
  }, [projectsData])

  // Group agents by project_name
  const groups = useMemo(() => {
    const agents = historyData?.agents ?? []

    const byProject = new Map<string, Agent[]>()
    for (const agent of agents) {
      const key = agent.project_name ?? '__unknown__'
      if (!byProject.has(key)) byProject.set(key, [])
      byProject.get(key)!.push(agent)
    }

    // Convert to array with project metadata
    const result: Array<{ key: string; project: Project | null; agents: Agent[] }> = []
    for (const [key, agentList] of byProject.entries()) {
      result.push({
        key,
        project: projectMap.get(key) ?? null,
        agents: agentList,
      })
    }

    // Sort: pinned projects first, then by most recent agent
    result.sort((a, b) => {
      const aPinned = a.project?.pinned ?? false
      const bPinned = b.project?.pinned ?? false
      if (aPinned && !bPinned) return -1
      if (!aPinned && bPinned) return 1

      const aTime = a.agents[0]?.started_at ?? a.agents[0]?.last_activity ?? ''
      const bTime = b.agents[0]?.started_at ?? b.agents[0]?.last_activity ?? ''
      return bTime.localeCompare(aTime)
    })

    return result
  }, [historyData, projectMap])

  return (
    <div className="max-w-6xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <div>
          <p className="eyebrow mb-1">Projects</p>
          <h1 className="text-h1 title-gradient">Timeline</h1>
        </div>
        {historyData && (
          <span className="ml-2 bg-white/5 border border-white/10 px-2.5 py-0.5 rounded-full text-xs font-medium text-text-muted tabular-nums">
            {historyData.agents.length} agents
          </span>
        )}
        <div className="ml-auto w-36">
          <GlassSelect
            value={timeRange}
            onChange={e => setTimeRange(e.target.value as TimeRange)}
          >
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="all">All time</option>
          </GlassSelect>
        </div>
      </div>

      {/* Loading skeletons */}
      {loading && !historyData && (
        <div className="space-y-3">
          {[0, 1, 2].map(i => (
            <div key={i} className="glass p-4">
              <Skeleton className="h-5 w-48 mb-3" />
              <Skeleton className="h-3 w-full mb-2" />
              <Skeleton className="h-3 w-4/5" />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && groups.length === 0 && (
        <div className="glass py-16 text-center text-text-subtle text-sm">
          No agents found for this time range.
        </div>
      )}

      {/* Project groups */}
      {groups.map(({ key, project, agents }) => {
        // Build a synthetic Project for unknown projects
        const effectiveProject: Project = project ?? {
          git_root: key,
          project_name: key,
          display_name: key === '__unknown__' ? 'Unknown Project' : key,
          color: '#6b7280',
          pinned: false,
          git_remote: null,
          agent_count: agents.length,
          session_count: 0,
          last_active: null,
          branches_seen: [],
          agent_types: {},
          status_summary: {},
        }

        return (
          <ProjectGroup
            key={key}
            project={effectiveProject}
            agents={agents}
            defaultExpanded={true}
          />
        )
      })}
    </div>
  )
}
