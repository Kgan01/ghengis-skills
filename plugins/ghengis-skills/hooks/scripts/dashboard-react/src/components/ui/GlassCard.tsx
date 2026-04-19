interface GlassCardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  hoverable?: boolean
  onClick?: () => void
}

export function GlassCard({ children, className = '', hover = false, hoverable = false, onClick }: GlassCardProps) {
  const isHoverable = hover || hoverable
  return (
    <div
      className={`glass ${isHoverable ? 'glass-hover cursor-pointer' : ''} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}
