import { useState, useEffect } from 'react'
import type { Permission } from '../../types'

interface Props {
  permissions: Permission[]
  onDecide: (id: string, approved: boolean) => void
}

function Countdown({ expiresAt }: { expiresAt: string }) {
  const [secondsLeft, setSecondsLeft] = useState(0)

  useEffect(() => {
    const update = () => {
      const left = Math.max(0, Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000))
      setSecondsLeft(left)
    }
    update()
    const id = setInterval(update, 1000)
    return () => clearInterval(id)
  }, [expiresAt])

  return <span className="text-xs text-text-subtle">{secondsLeft}s</span>
}

export function PermissionToast({ permissions, onDecide }: Props) {
  if (permissions.length === 0) return null

  const visible = permissions.slice(0, 3)
  const overflow = permissions.length - 3

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 items-end">
      {visible.map(p => (
        <div key={p.id} className="glass p-4 max-w-[360px] animate-slide-in" style={{ borderColor: 'rgba(251,191,36,0.3)' }}>
          <div className="flex items-center justify-between mb-2">
            <span className="eyebrow">{p.tool_name}</span>
            <Countdown expiresAt={p.expires_at} />
          </div>
          <p className="text-xs text-text-muted font-mono line-clamp-3 mb-3">{p.input_preview}</p>
          <div className="flex gap-2">
            <button
              onClick={() => onDecide(p.id, true)}
              className="flex-1 px-3 py-1.5 text-sm font-medium rounded-lg bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/30 transition-colors"
            >
              Approve
            </button>
            <button
              onClick={() => onDecide(p.id, false)}
              className="flex-1 px-3 py-1.5 text-sm font-medium rounded-lg bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 transition-colors"
            >
              Deny
            </button>
          </div>
        </div>
      ))}
      {overflow > 0 && (
        <span className="text-xs text-text-subtle">+{overflow} more</span>
      )}
    </div>
  )
}
