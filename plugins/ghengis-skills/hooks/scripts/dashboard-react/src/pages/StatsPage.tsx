import { useStats } from '../hooks/useStats'
import { useAgents } from '../hooks/useAgents'
import { StatCard } from '../components/ui/StatCard'
import { StatCardSkeleton } from '../components/ui/Skeleton'
import { GlassCard } from '../components/ui/GlassCard'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#6b7fff', '#06b6d4', '#a78bfa', '#34d399', '#f59e0b', '#ef4444']

function formatSeconds(secs: number): string {
  if (secs < 60) return `${Math.round(secs)}s`
  return `${Math.floor(secs / 60)}m ${Math.round(secs % 60)}s`
}

export function StatsPage() {
  const { stats, loading } = useStats()
  const { data: liveData } = useAgents(5000)

  if (loading || !stats) {
    return (
      <div className="max-w-4xl">
        <h1 className="text-2xl text-h1 title-gradient mb-6">Stats</h1>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <StatCardSkeleton key={i} />)}
        </div>
      </div>
    )
  }

  const topModel = Object.entries(stats.by_model).sort((a, b) => b[1] - a[1])[0]
  const dateData = Object.entries(stats.by_date).map(([date, count]) => ({
    date: date.slice(5), // MM-DD
    count,
  }))
  const modelData = Object.entries(stats.by_model).map(([name, value]) => ({ name, value }))

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl text-h1 title-gradient mb-6">Stats</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Agents" value={stats.total} />
        <StatCard label="Running Now" value={liveData?.running_count ?? 0} />
        <StatCard label="Avg Duration" value={formatSeconds(stats.avg_duration_seconds)} />
        <StatCard label="Top Model" value={topModel ? topModel[0] : '-'} subtitle={topModel ? `${topModel[1]} agents` : undefined} />
      </div>

      {dateData.length > 0 && (
        <GlassCard className="p-6 mb-6">
          <h3 className="text-xs uppercase tracking-wider text-text-subtle mb-4">Agents per Day (Last 30 Days)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={dateData}>
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#6b7fff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </GlassCard>
      )}

      {modelData.length > 0 && (
        <GlassCard className="p-6">
          <h3 className="text-xs uppercase tracking-wider text-text-subtle mb-4">Model Distribution</h3>
          <div className="flex items-center gap-8">
            <ResponsiveContainer width={200} height={200}>
              <PieChart>
                <Pie data={modelData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" paddingAngle={2}>
                  {modelData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-col gap-2">
              {modelData.map((d, i) => (
                <div key={d.name} className="flex items-center gap-2 text-sm">
                  <span className="w-3 h-3 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                  <span className="text-text-base">{d.name}</span>
                  <span className="text-text-subtle ml-auto">{d.value}</span>
                </div>
              ))}
            </div>
          </div>
        </GlassCard>
      )}
    </div>
  )
}
