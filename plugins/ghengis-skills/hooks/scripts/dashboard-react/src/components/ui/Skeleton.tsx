import { GlassCard } from './GlassCard'

export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-white/10 ${className}`} />
}

export function AgentCardSkeleton() {
  return (
    <GlassCard className="p-4">
      <div className="flex items-center gap-3 mb-3">
        <Skeleton className="h-5 w-16 rounded-full" />
        <Skeleton className="h-5 w-14 rounded-full" />
        <Skeleton className="h-5 w-20 rounded-full" />
      </div>
      <Skeleton className="h-3 w-full mb-2" />
      <Skeleton className="h-3 w-4/5 mb-3" />
      <div className="flex gap-2">
        <Skeleton className="h-5 w-12 rounded-full" />
        <Skeleton className="h-5 w-14 rounded-full" />
      </div>
    </GlassCard>
  )
}

export function StatCardSkeleton() {
  return (
    <GlassCard className="p-3 md:p-6">
      <Skeleton className="h-3 w-20 mb-2" />
      <Skeleton className="h-8 w-14" />
    </GlassCard>
  )
}
