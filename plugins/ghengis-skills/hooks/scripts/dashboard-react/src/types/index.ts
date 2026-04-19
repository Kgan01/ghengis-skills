export interface ToolCall {
  name: string
  input: Record<string, unknown>
  timestamp: string
}

export interface Message {
  type: 'text' | 'tool_result'
  content: string
  timestamp: string
}

export interface Agent {
  id: string
  type: string
  model: string
  prompt: string
  status: 'running' | 'completed'
  started_at: string | null
  ended_at: string | null
  tool_calls: ToolCall[]
  messages: Message[]
  last_activity: string
  session_id?: string
  tool_call_count?: number
  message_count?: number
  cwd?: string
  git_root?: string
  project_name?: string
  git_branch?: string
  git_remote?: string
}

export interface AgentsResponse {
  agents: Agent[]
  running_count: number
  total_count: number
  timestamp: string
}

export interface HistoryResponse {
  agents: Agent[]
  total: number
  limit: number
  offset: number
}

export interface Permission {
  id: string
  tool_name: string
  input_preview: string
  created_at: string
  status: 'pending' | 'approved' | 'denied'
  expires_at: string
}

export interface Stats {
  total: number
  by_model: Record<string, number>
  by_type: Record<string, number>
  by_date: Record<string, number>
  avg_duration_seconds: number
}

export interface Project {
  git_root: string
  project_name: string
  display_name: string
  color: string
  pinned: boolean
  git_remote: string | null
  agent_count: number
  session_count: number
  last_active: string | null
  branches_seen: string[]
  agent_types: Record<string, number>
  status_summary: Record<string, number>
}

export interface ProjectSettings {
  display_name?: string
  color?: string
  pinned?: boolean
}

export interface ProjectsResponse {
  projects: Project[]
}

export interface ProjectAgentsResponse {
  agents: Agent[]
  total: number
}
