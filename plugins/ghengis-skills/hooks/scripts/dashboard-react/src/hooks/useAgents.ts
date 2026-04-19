import { useState, useEffect } from 'react'
import type { AgentsResponse } from '../types'

export function useAgents(intervalMs: number | null = 1000) {
  const [data, setData] = useState<AgentsResponse | null>(null)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false
    const poll = async () => {
      try {
        const res = await fetch('/api/agents')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()
        if (!cancelled) { setData(json); setError(null) }
      } catch (e) {
        if (!cancelled) setError(e as Error)
      }
    }
    poll()
    if (intervalMs == null || intervalMs <= 0) {
      return () => { cancelled = true }
    }
    const id = setInterval(poll, intervalMs)
    return () => { cancelled = true; clearInterval(id) }
  }, [intervalMs])

  return { data, error }
}
