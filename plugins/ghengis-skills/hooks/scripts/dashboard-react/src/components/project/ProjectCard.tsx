import { Link } from 'react-router-dom'
import type { Project } from '../../types'
import { Badge } from '../ui/Badge'

interface ProjectCardProps {
  project: Project
}

export function ProjectCard({ project }: ProjectCardProps) {
  const topTypes = Object.entries(project.agent_types)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)

  return (
    <Link
      to={`/projects/${encodeURIComponent(project.project_name)}`}
      className="glass rounded-xl p-5 block hover:bg-white/[0.04] transition-colors group"
      style={{ borderLeft: `3px solid ${project.color}` }}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-text-high font-medium text-sm group-hover:text-primary-400 transition-colors">
            {project.display_name}
            {project.pinned && <span className="ml-2 text-text-subtle text-xs">pinned</span>}
          </h3>
          {project.git_remote && (
            <p className="text-text-subtle text-xs mt-0.5 truncate max-w-[250px]">
              {project.git_remote}
            </p>
          )}
        </div>
        <span className="text-text-muted text-xs tabular-nums">
          {project.agent_count} agents
        </span>
      </div>

      <div className="flex gap-4 text-xs text-text-muted mb-3">
        <span>{project.session_count} sessions</span>
        {project.last_active && (
          <span>Last active: {new Date(project.last_active).toLocaleDateString()}</span>
        )}
      </div>

      <div className="flex flex-wrap gap-1.5 mb-3">
        {project.branches_seen.slice(0, 5).map(branch => (
          <Badge key={branch} label={branch} variant="tool" />
        ))}
        {project.branches_seen.length > 5 && (
          <span className="text-text-subtle text-xs">+{project.branches_seen.length - 5}</span>
        )}
      </div>

      <div className="flex gap-1.5">
        {topTypes.map(([type, count]) => (
          <Badge key={type} label={`${type}: ${count}`} variant="type" />
        ))}
      </div>

      {project.status_summary && (
        <div className="flex gap-3 mt-3 pt-3 border-t border-white/5 text-xs text-text-subtle">
          {Object.entries(project.status_summary).map(([status, count]) => (
            <span key={status}>{status}: {count}</span>
          ))}
        </div>
      )}
    </Link>
  )
}
