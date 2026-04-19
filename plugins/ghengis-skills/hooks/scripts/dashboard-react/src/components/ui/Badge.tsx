const MODEL_COLORS: Record<string, string> = {
  opus: 'badge-opus',
  sonnet: 'badge-sonnet',
  haiku: 'badge-haiku',
}

const STATUS_COLORS: Record<string, string> = {
  running: 'badge-running',
  completed: 'badge-completed',
  failed: 'badge-failed',
}

const TYPE_COLORS: Record<string, string> = {
  'general-purpose': 'bg-blue-500/20 text-blue-300 border border-blue-500/30',
  'Explore': 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30',
  'Plan': 'bg-violet-500/20 text-violet-300 border border-violet-500/30',
  'frontend-design': 'bg-pink-500/20 text-pink-300 border border-pink-500/30',
}

interface BadgeProps {
  label: string
  variant?: 'model' | 'status' | 'type' | 'tool'
}

export function Badge({ label, variant = 'type' }: BadgeProps) {
  let colorClass = 'bg-gray-500/20 text-gray-300 border border-gray-500/30'

  if (variant === 'model') {
    const key = label.toLowerCase()
    for (const [model, cls] of Object.entries(MODEL_COLORS)) {
      if (key.includes(model)) { colorClass = cls; break }
    }
  } else if (variant === 'status') {
    colorClass = STATUS_COLORS[label] || colorClass
  } else if (variant === 'type') {
    colorClass = TYPE_COLORS[label] || colorClass
  } else if (variant === 'tool') {
    colorClass = 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
      {variant === 'status' && label === 'running' && (
        <span className="inline-block w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse-dot mr-1.5" />
      )}
      {label}
    </span>
  )
}
