import { Link, useParams } from 'react-router-dom'
import { Badge } from '../ui/Badge'
import { Skeleton } from '../ui/Skeleton'
import { useProjects } from '../../hooks/useProjects'
import type { Project } from '../../types'

function formatLastActive(lastActive: string | null): string {
  if (!lastActive) return 'never'
  const date = new Date(lastActive)
  const now = Date.now()
  const diffMs = now - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

interface ProjectItemProps {
  project: Project
  isActive: boolean
}

function ProjectItem({ project, isActive }: ProjectItemProps) {
  return (
    <Link
      to={`/projects/${encodeURIComponent(project.project_name)}`}
      className={`block px-3 py-2.5 rounded-lg transition-colors group ${
        isActive
          ? 'bg-[rgba(120,150,255,0.12)] border border-[rgba(120,150,255,0.3)]'
          : 'hover:bg-[rgba(200,210,255,0.04)] border border-transparent'
      }`}
    >
      <div className="flex items-center justify-between gap-2 mb-1">
        <span
          className={`text-sm font-medium truncate ${
            isActive ? 'text-text-high' : 'text-text-muted group-hover:text-text-high'
          }`}
        >
          {project.display_name}
        </span>
        <Badge label={String(project.agent_count)} variant="type" />
      </div>
      <div className="text-xs text-text-subtle">
        {formatLastActive(project.last_active)}
      </div>
    </Link>
  )
}

export function ProjectSidebar() {
  const { name: projectName } = useParams<{ name: string }>()
  const { data, loading } = useProjects()

  return (
    <aside className="w-64 flex-shrink-0 flex flex-col gap-2">
      <div className="mb-2">
        <Link
          to="/projects"
          className="inline-flex items-center gap-1.5 text-xs text-text-subtle hover:text-text-muted transition-colors"
        >
          <svg
            className="w-3.5 h-3.5"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M10 3L5 8l5 5"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          All Projects
        </Link>
      </div>

      <div className="glass rounded-xl p-3 flex flex-col gap-1">
        <p className="eyebrow px-3 pb-2">Projects</p>

        {loading && (
          <div className="flex flex-col gap-2 px-1">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="px-2 py-2.5">
                <Skeleton className="h-4 w-3/4 mb-1.5" />
                <Skeleton className="h-3 w-1/3" />
              </div>
            ))}
          </div>
        )}

        {!loading && data?.projects.length === 0 && (
          <p className="text-xs text-text-subtle px-3 py-2">No projects found</p>
        )}

        {!loading && data?.projects.map((project) => (
          <ProjectItem
            key={project.project_name}
            project={project}
            isActive={decodeURIComponent(projectName || '') === project.project_name}
          />
        ))}
      </div>
    </aside>
  )
}
