import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { ProjectSidebar } from '../components/project/ProjectSidebar'
import AgentRow from '../components/agent/AgentRow'
import { GlassSelect } from '../components/ui/GlassSelect'
import { AgentCardSkeleton } from '../components/ui/Skeleton'
import { useProjectAgents } from '../hooks/useProjectAgents'
import type { Agent } from '../types'

export default function ProjectSidebarPage() {
  const { name: projectName } = useParams<{ name: string }>()
  const decodedName = projectName ? decodeURIComponent(projectName) : undefined

  const { data, loading, fetchAgents } = useProjectAgents(decodedName)

  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [branchFilter, setBranchFilter] = useState<string>('all')

  useEffect(() => {
    if (decodedName) {
      fetchAgents()
      setExpandedId(null)
      setTypeFilter('all')
      setBranchFilter('all')
    }
  }, [decodedName, fetchAgents])

  const agents: Agent[] = data?.agents || []

  // Derive unique types and branches for filter options
  const agentTypes = Array.from(new Set(agents.map((a) => a.type).filter(Boolean)))
  const branches = Array.from(new Set(agents.map((a) => a.git_branch).filter(Boolean))) as string[]

  const filtered = agents.filter((a) => {
    if (typeFilter !== 'all' && a.type !== typeFilter) return false
    if (branchFilter !== 'all' && a.git_branch !== branchFilter) return false
    return true
  })

  return (
    <div className="flex gap-6 min-h-screen p-6">
      <ProjectSidebar />

      <main className="flex-1 min-w-0">
        {!decodedName ? (
          <div className="flex flex-col items-center justify-center h-64 gap-3">
            <p className="text-text-muted text-lg">Select a project</p>
            <p className="text-text-subtle text-sm">Choose a project from the sidebar to view its agents</p>
          </div>
        ) : (
          <>
            <div className="mb-6">
              <p className="eyebrow mb-1">Project</p>
              <h1 className="text-h1 title-gradient">{decodedName}</h1>
            </div>

            <div className="flex gap-4 mb-6">
              <div className="w-48">
                <GlassSelect
                  label="Agent type"
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                >
                  <option value="all">All types</option>
                  {agentTypes.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </GlassSelect>
              </div>

              <div className="w-48">
                <GlassSelect
                  label="Branch"
                  value={branchFilter}
                  onChange={(e) => setBranchFilter(e.target.value)}
                >
                  <option value="all">All branches</option>
                  {branches.map((b) => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </GlassSelect>
              </div>
            </div>

            <div className="glass rounded-xl overflow-hidden">
              {loading && (
                <div className="flex flex-col gap-3 p-4">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <AgentCardSkeleton key={i} />
                  ))}
                </div>
              )}

              {!loading && filtered.length === 0 && (
                <div className="flex flex-col items-center justify-center py-16 gap-3">
                  <p className="text-text-muted">No agents found</p>
                  <p className="text-text-subtle text-sm">
                    {agents.length > 0
                      ? 'Try adjusting the filters'
                      : 'No agents have run in this project yet'}
                  </p>
                </div>
              )}

              {!loading && filtered.length > 0 && (
                <div>
                  {filtered.map((agent) => (
                    <AgentRow
                      key={agent.id}
                      agent={agent}
                      expanded={expandedId === agent.id}
                      onToggle={() => setExpandedId(expandedId === agent.id ? null : agent.id)}
                    />
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
