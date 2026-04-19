import { GlassCard } from './GlassCard'

interface StatCardProps {
  label: string
  value: number | string
  subtitle?: string
}

export function StatCard({ label, value, subtitle }: StatCardProps) {
  return (
    <GlassCard className="p-3 md:p-6">
      <p className="text-xs md:text-sm text-text-muted font-medium uppercase tracking-wider">{label}</p>
      <p className="mt-1 md:mt-2 text-xl md:text-3xl font-medium tracking-tight title-gradient font-heading">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </p>
      {subtitle && <p className="mt-1 text-xs text-text-subtle">{subtitle}</p>}
    </GlassCard>
  )
}
