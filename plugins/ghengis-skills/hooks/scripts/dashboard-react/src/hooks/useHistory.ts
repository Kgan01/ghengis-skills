import { useState, useEffect, useCallback } from 'react'
import type { Agent, HistoryResponse } from '../types'

interface Filters {
  q?: string
  date_from?: string
  date_to?: string
  type?: string
  model?: string
  limit?: number
  offset?: number
}

export function useHistory(filters: Filters = {}) {
  const [data, setData] = useState<HistoryResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchHistory = useCallback(async (f: Filters) => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (f.q) params.set('q', f.q)
      if (f.date_from) params.set('date_from', f.date_from)
      if (f.date_to) params.set('date_to', f.date_to)
      if (f.type) params.set('type', f.type)
      if (f.model) params.set('model', f.model)
      params.set('limit', String(f.limit || 50))
      params.set('offset', String(f.offset || 0))

      const res = await fetch(`/api/history?${params}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      setData(json)
    } catch (e) {
      console.error('History fetch failed:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchHistory(filters)
  }, [filters.q, filters.date_from, filters.date_to, filters.type, filters.model, filters.limit, filters.offset])

  const fetchAgent = useCallback(async (id: string): Promise<Agent | null> => {
    try {
      const res = await fetch(`/api/history/${id}`)
      if (!res.ok) return null
      return await res.json()
    } catch {
      return null
    }
  }, [])

  return { data, loading, fetchHistory, fetchAgent }
}
