import { useState, useMemo } from 'react'
import { useProjects } from '../hooks/useProjects'
import { ProjectCard } from '../components/project/ProjectCard'
import { ProjectSettingsModal } from '../components/project/ProjectSettingsModal'
import { GlassInput } from '../components/ui/GlassInput'
import { GlassSelect } from '../components/ui/GlassSelect'
import { Skeleton } from '../components/ui/Skeleton'
import type { Project } from '../types'

type SortKey = 'last_active' | 'agent_count' | 'name'

function ProjectCardSkeleton() {
  return (
    <div className="glass rounded-xl p-5" style={{ borderLeft: '3px solid rgba(107,127,255,0.3)' }}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <Skeleton className="h-4 w-40 mb-1.5" />
          <Skeleton className="h-3 w-56" />
        </div>
        <Skeleton className="h-3 w-14" />
      </div>
      <div className="flex gap-4 mb-3">
        <Skeleton className="h-3 w-20" />
        <Skeleton className="h-3 w-28" />
      </div>
      <div className="flex gap-1.5 mb-3">
        <Skeleton className="h-5 w-16 rounded-full" />
        <Skeleton className="h-5 w-14 rounded-full" />
        <Skeleton className="h-5 w-18 rounded-full" />
      </div>
      <div className="flex gap-1.5">
        <Skeleton className="h-5 w-20 rounded-full" />
        <Skeleton className="h-5 w-16 rounded-full" />
      </div>
    </div>
  )
}

interface ProjectCardWrapperProps {
  project: Project
  onSettings: (project: Project) => void
}

function ProjectCardWrapper({ project, onSettings }: ProjectCardWrapperProps) {
  return (
    <div className="relative group/wrapper">
      <ProjectCard project={project} />
      <button
        className="absolute top-3 right-3 opacity-0 group-hover/wrapper:opacity-100 transition-opacity z-10 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-text-subtle hover:text-text-high"
        onClick={e => {
          e.preventDefault()
          e.stopPropagation()
          onSettings(project)
        }}
        title="Project settings"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      </button>
    </div>
  )
}

export function ProjectCardsPage() {
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('last_active')
  const [settingsProject, setSettingsProject] = useState<Project | null>(null)

  const { data, loading, fetchProjects } = useProjects()

  const filtered = useMemo(() => {
    if (!data?.projects) return []

    const q = search.trim().toLowerCase()
    let list = q
      ? data.projects.filter(p =>
          p.display_name.toLowerCase().includes(q) ||
          p.project_name.toLowerCase().includes(q) ||
          (p.git_remote?.toLowerCase().includes(q) ?? false)
        )
      : [...data.projects]

    list.sort((a, b) => {
      if (sortKey === 'last_active') {
        const aTime = a.last_active ? new Date(a.last_active).getTime() : 0
        const bTime = b.last_active ? new Date(b.last_active).getTime() : 0
        return bTime - aTime
      }
      if (sortKey === 'agent_count') {
        return b.agent_count - a.agent_count
      }
      return a.display_name.localeCompare(b.display_name)
    })

    // pinned projects always float to the top
    const pinned = list.filter(p => p.pinned)
    const unpinned = list.filter(p => !p.pinned)
    return [...pinned, ...unpinned]
  }, [data, search, sortKey])

  return (
    <div className="max-w-6xl">
      <div className="flex items-center gap-4 mb-6">
        <h1 className="text-h1 title-gradient">Projects</h1>
        {data && (
          <span className="bg-white/5 border border-white/10 px-2.5 py-0.5 rounded-full text-xs font-medium text-text-muted">
            {data.projects.length} projects
          </span>
        )}
      </div>

      <div className="flex flex-wrap gap-3 mb-6">
        <div className="flex-1 min-w-[200px]">
          <GlassInput
            placeholder="Search by name or remote..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="w-44">
          <GlassSelect
            value={sortKey}
            onChange={e => setSortKey(e.target.value as SortKey)}
          >
            <option value="last_active">Last active</option>
            <option value="agent_count">Agent count</option>
            <option value="name">Name</option>
          </GlassSelect>
        </div>
      </div>

      {loading && !data && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <ProjectCardSkeleton key={i} />
          ))}
        </div>
      )}

      {data && filtered.length === 0 && (
        <div className="py-20 text-center">
          <p className="text-text-muted text-sm">
            {search ? 'No projects match your search.' : 'No projects found.'}
          </p>
        </div>
      )}

      {data && filtered.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(project => (
            <ProjectCardWrapper
              key={project.project_name}
              project={project}
              onSettings={setSettingsProject}
            />
          ))}
        </div>
      )}

      {settingsProject && (
        <ProjectSettingsModal
          project={settingsProject}
          onClose={() => setSettingsProject(null)}
          onSave={fetchProjects}
        />
      )}
    </div>
  )
}
