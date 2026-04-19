import { useState, useEffect } from 'react'
import { GlassButton } from '../ui/GlassButton'
import type { Permission } from '../../types'

interface Props {
  permission: Permission
  onDecide: (id: string, approved: boolean) => void
}

export function PermissionCard({ permission, onDecide }: Props) {
  const [secondsLeft, setSecondsLeft] = useState(0)

  useEffect(() => {
    const update = () => {
      const expires = new Date(permission.expires_at).getTime()
      const left = Math.max(0, Math.floor((expires - Date.now()) / 1000))
      setSecondsLeft(left)
    }
    update()
    const id = setInterval(update, 1000)
    return () => clearInterval(id)
  }, [permission.expires_at])

  return (
    <div className="glass p-4 animate-permission-glow" style={{ borderColor: 'rgba(251,191,36,0.3)' }}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse-dot" />
            <span className="text-sm font-semibold text-amber-400">Permission Required</span>
            <span className="text-xs text-text-subtle ml-auto">{secondsLeft}s remaining</span>
          </div>
          <p className="text-sm text-text-high font-medium mb-1">{permission.tool_name}</p>
          <p className="text-xs text-text-muted font-mono break-all">{permission.input_preview}</p>
        </div>
        <div className="flex gap-2 shrink-0">
          <GlassButton variant="primary" onClick={() => onDecide(permission.id, true)} className="!px-3 !py-1.5 text-sm">
            Approve
          </GlassButton>
          <GlassButton variant="danger" onClick={() => onDecide(permission.id, false)} className="!px-3 !py-1.5 text-sm">
            Deny
          </GlassButton>
        </div>
      </div>
    </div>
  )
}
