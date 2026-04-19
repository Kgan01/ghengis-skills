import { useState, useEffect, useCallback } from 'react'
import type { Permission } from '../types'

export function usePermissions(intervalMs = 2000) {
  const [permissions, setPermissions] = useState<Permission[]>([])

  useEffect(() => {
    let cancelled = false
    const poll = async () => {
      try {
        const res = await fetch('/api/permissions')
        if (!res.ok) return
        const json = await res.json()
        if (!cancelled) setPermissions(json.permissions || [])
      } catch { /* ignore */ }
    }
    poll()
    const id = setInterval(poll, intervalMs)
    return () => { cancelled = true; clearInterval(id) }
  }, [intervalMs])

  const decide = useCallback(async (id: string, approved: boolean) => {
    try {
      await fetch(`/api/permissions/${id}/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved })
      })
      setPermissions(prev => prev.filter(p => p.id !== id))
    } catch (e) {
      console.error('Permission decision failed:', e)
    }
  }, [])

  return { permissions, decide }
}
