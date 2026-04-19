import { useState, useCallback } from 'react'
import type { ProjectAgentsResponse } from '../types'

export function useProjectAgents(projectName: string | undefined) {
  const [data, setData] = useState<ProjectAgentsResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchAgents = useCallback(async () => {
    if (!projectName) return
    setLoading(true)
    try {
      const res = await fetch(`/api/projects/${encodeURIComponent(projectName)}/agents`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setData(await res.json())
    } catch (e) {
      console.error('Project agents fetch failed:', e)
    } finally {
      setLoading(false)
    }
  }, [projectName])

  return { data, loading, fetchAgents }
}
