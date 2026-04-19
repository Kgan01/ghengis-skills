import { useState, useMemo } from 'react'
import type { ToolCall, Message } from '../../types'

interface TimelineItem {
  type: 'tool' | 'text' | 'result'
  name?: string
  input?: Record<string, unknown>
  content?: string
  timestamp: string
  durationMs?: number
}

function formatOffset(timestamp: string, refTime?: string): string {
  if (!refTime) return ''
  const t = new Date(timestamp).getTime()
  const ref = new Date(refTime).getTime()
  const diff = Math.floor((t - ref) / 1000)
  if (diff < 0) return '+0s'
  if (diff < 60) return `+${diff}s`
  if (diff < 3600) return `+${Math.floor(diff / 60)}m ${diff % 60}s`
  return `+${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`
}

function extractFilePath(input?: Record<string, unknown>): string | null {
  if (!input) return null
  for (const key of ['file_path', 'path', 'file']) {
    if (typeof input[key] === 'string') return input[key] as string
  }
  if (typeof input['command'] === 'string') {
    const cmd = input['command'] as string
    if (cmd.length < 200) return cmd
  }
  return null
}

function CollapsibleJson({ data, externalExpanded, onToggle }: {
  data: Record<string, unknown>
  externalExpanded?: boolean
  onToggle?: () => void
}) {
  const [localExpanded, setLocalExpanded] = useState(false)
  const expanded = externalExpanded ?? localExpanded
  const toggle = onToggle ?? (() => setLocalExpanded(!localExpanded))

  const json = JSON.stringify(data, null, 2)
  const isLong = json.length > 200

  return (
    <div className="mt-2">
      <pre className="bg-[rgba(200,210,255,0.04)] rounded-lg p-3 text-xs text-text-base overflow-x-auto whitespace-pre-wrap"
           style={{ maxHeight: expanded ? 'none' : (isLong ? '80px' : 'none') }}>
        {json}
      </pre>
      {isLong && (
        <button
          onClick={(e) => { e.stopPropagation(); toggle() }}
          className="text-xs text-primary-400 mt-1 hover:text-primary-300"
        >
          {expanded ? 'Collapse' : 'Expand'}
        </button>
      )}
    </div>
  )
}

interface Props {
  toolCalls: ToolCall[]
  messages: Message[]
  startedAt?: string | null
}

export function AgentTimeline({ toolCalls, messages, startedAt }: Props) {
  const [expandedSet, setExpandedSet] = useState<Set<number>>(new Set())
  const [allExpanded, setAllExpanded] = useState(false)

  const items: TimelineItem[] = useMemo(() => {
    const result: TimelineItem[] = []

    for (const tc of toolCalls) {
      result.push({ type: 'tool', name: tc.name, input: tc.input, timestamp: tc.timestamp })
    }
    for (const m of messages) {
      result.push({
        type: m.type === 'tool_result' ? 'result' : 'text',
        content: m.content,
        timestamp: m.timestamp,
      })
    }

    result.sort((a, b) => {
      if (!a.timestamp) return 1
      if (!b.timestamp) return -1
      return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    })

    // Compute per-tool duration by pairing with next item
    for (let i = 0; i < result.length; i++) {
      if (result[i].type === 'tool' && i + 1 < result.length) {
        const next = result[i + 1]
        if (next.timestamp && result[i].timestamp) {
          const delta = new Date(next.timestamp).getTime() - new Date(result[i].timestamp).getTime()
          if (delta >= 0 && delta < 600000) {
            result[i].durationMs = delta
          }
        }
      }
    }

    return result
  }, [toolCalls, messages])

  if (items.length === 0) {
    return <p className="text-text-subtle text-sm">No activity recorded yet</p>
  }

  const toggleItem = (idx: number) => {
    setExpandedSet(prev => {
      const next = new Set(prev)
      if (next.has(idx)) next.delete(idx)
      else next.add(idx)
      return next
    })
    setAllExpanded(false)
  }

  const expandAll = () => {
    setExpandedSet(new Set(items.map((_, i) => i)))
    setAllExpanded(true)
  }

  const collapseAll = () => {
    setExpandedSet(new Set())
    setAllExpanded(false)
  }

  const isExpanded = (idx: number) => allExpanded || expandedSet.has(idx)

  const borderColors = { tool: 'border-l-emerald-400', text: 'border-l-blue-400', result: 'border-l-gray-500' }
  const typeLabels = { tool: 'Tool', text: 'Response', result: 'Result' }
  const typeColors = { tool: 'text-emerald-400', text: 'text-blue-400', result: 'text-gray-400' }

  return (
    <div>
      <div className="flex gap-3 mb-3">
        <button onClick={expandAll} className="eyebrow hover:text-primary-300 transition-colors">
          Expand All
        </button>
        <button onClick={collapseAll} className="eyebrow hover:text-primary-300 transition-colors">
          Collapse All
        </button>
      </div>
      <div className="flex flex-col gap-3">
        {items.map((item, i) => {
          const filePath = item.type === 'tool' ? extractFilePath(item.input) : null

          return (
            <div key={i} className={`glass p-4 border-l-4 ${borderColors[item.type]}`}>
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold uppercase ${typeColors[item.type]}`}>
                    {typeLabels[item.type]}{item.name ? `: ${item.name}` : ''}
                  </span>
                  {item.durationMs !== undefined && (
                    <span className="text-xs text-text-subtle font-mono">{item.durationMs}ms</span>
                  )}
                </div>
                <span className="text-xs text-text-subtle">
                  {item.timestamp ? formatOffset(item.timestamp, startedAt || undefined) : ''}
                </span>
              </div>
              {filePath && (
                <div className="mb-2">
                  <span className="font-mono text-[#6b7fff] text-sm">{filePath}</span>
                </div>
              )}
              {item.type === 'tool' && item.input && (
                <CollapsibleJson
                  data={item.input}
                  externalExpanded={isExpanded(i)}
                  onToggle={() => toggleItem(i)}
                />
              )}
              {(item.type === 'text' || item.type === 'result') && item.content && (
                <div className="text-sm text-text-base whitespace-pre-wrap break-words"
                     style={{ maxHeight: item.type === 'result' ? '200px' : 'none', overflowY: item.type === 'result' ? 'auto' : 'visible' }}>
                  {item.content}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
