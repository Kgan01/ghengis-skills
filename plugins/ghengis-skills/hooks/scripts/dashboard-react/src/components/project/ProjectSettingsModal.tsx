import { useState } from 'react'
import type { Project } from '../../types'
import { GlassButton } from '../ui/GlassButton'
import { GlassInput } from '../ui/GlassInput'

interface ProjectSettingsModalProps {
  project: Project
  onClose: () => void
  onSave: () => void
}

const PRESET_COLORS = [
  '#6b7fff', '#f472b6', '#34d399', '#fbbf24', '#a78bfa',
  '#fb923c', '#22d3ee', '#f87171', '#4ade80', '#c084fc',
]

export function ProjectSettingsModal({ project, onClose, onSave }: ProjectSettingsModalProps) {
  const [displayName, setDisplayName] = useState(project.display_name)
  const [color, setColor] = useState(project.color)
  const [pinned, setPinned] = useState(project.pinned)
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    setSaving(true)
    try {
      const res = await fetch(`/api/projects/${encodeURIComponent(project.project_name)}/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ display_name: displayName, color, pinned }),
      })
      if (res.ok) {
        onSave()
        onClose()
      }
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="glass rounded-xl p-6 w-full max-w-md" onClick={e => e.stopPropagation()}>
        <h2 className="text-h2 text-text-high mb-4">Project Settings</h2>
        <p className="text-text-subtle text-xs mb-4">{project.git_root}</p>

        <label className="block mb-3">
          <span className="eyebrow block mb-1">Display Name</span>
          <GlassInput value={displayName} onChange={e => setDisplayName(e.target.value)} />
        </label>

        <div className="mb-3">
          <span className="eyebrow block mb-1">Color</span>
          <div className="flex gap-2 flex-wrap">
            {PRESET_COLORS.map(c => (
              <button
                key={c}
                className={`w-7 h-7 rounded-full border-2 transition-all ${
                  color === c ? 'border-white scale-110' : 'border-transparent'
                }`}
                style={{ backgroundColor: c }}
                onClick={() => setColor(c)}
              />
            ))}
          </div>
        </div>

        <label className="flex items-center gap-2 mb-6 cursor-pointer">
          <input
            type="checkbox"
            checked={pinned}
            onChange={e => setPinned(e.target.checked)}
            className="w-4 h-4 rounded"
          />
          <span className="text-text-muted text-sm">Pin to top</span>
        </label>

        <div className="flex gap-2 justify-end">
          <GlassButton variant="secondary" onClick={onClose}>Cancel</GlassButton>
          <GlassButton onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </GlassButton>
        </div>
      </div>
    </div>
  )
}
