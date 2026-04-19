import { useState, useEffect } from 'react'
import type { Stats } from '../types'

export function useStats() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('/api/stats')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()
        setStats(json)
      } catch (e) {
        console.error('Stats fetch failed:', e)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  return { stats, loading }
}
