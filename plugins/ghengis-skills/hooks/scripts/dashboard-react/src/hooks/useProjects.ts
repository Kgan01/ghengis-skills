import { useState, useEffect, useCallback } from 'react'
import type { ProjectsResponse } from '../types'

export function useProjects() {
  const [data, setData] = useState<ProjectsResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchProjects = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/projects')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setData(await res.json())
    } catch (e) {
      console.error('Projects fetch failed:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchProjects() }, [fetchProjects])

  return { data, loading, fetchProjects }
}
