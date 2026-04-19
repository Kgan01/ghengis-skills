import { useState, useEffect, useMemo } from 'react'
import { useHistory } from '../hooks/useHistory'
import { AgentCard } from '../components/agent/AgentCard'
import { GlassInput } from '../components/ui/GlassInput'
import { GlassCard } from '../components/ui/GlassCard'

export function SearchPage() {
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 400)
    return () => clearTimeout(t)
  }, [search])

  const filters = useMemo(() => ({
    q: debouncedSearch || undefined,
    limit: 50,
  }), [debouncedSearch])

  const { data, loading } = useHistory(debouncedSearch ? filters : {})

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl text-h1 title-gradient mb-6">Search</h1>

      <div className="mb-6">
        <GlassInput
          placeholder="Search across all agent prompts and transcripts..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          autoFocus
          className="!text-lg !py-4"
        />
      </div>

      {!debouncedSearch && (
        <GlassCard className="p-12 text-center">
          <p className="text-text-muted">Search across all agent prompts and transcripts</p>
        </GlassCard>
      )}

      {debouncedSearch && loading && (
        <p className="text-text-subtle text-center py-8">Searching...</p>
      )}

      {debouncedSearch && data && data.agents.length === 0 && (
        <p className="text-text-subtle text-center py-8">No results for "{debouncedSearch}"</p>
      )}

      {debouncedSearch && data && data.agents.length > 0 && (
        <div className="flex flex-col gap-3">
          <p className="text-xs text-text-subtle mb-2">{data.total} results</p>
          {data.agents.map(agent => <AgentCard key={agent.id} agent={agent} />)}
        </div>
      )}
    </div>
  )
}
