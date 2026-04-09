import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'

function riskColor(score: number | null | undefined) {
  if (score == null) return '#9ca3af'
  if (score >= 7) return '#f87171'
  if (score >= 4) return '#fbbf24'
  return '#34d399'
}

type RunEntry = {
  timestamp: number
  repo: string
  risk_score?: number | null
  top_contributor_pct?: number | null
  effective_contributors?: number | null
  label?: string
}

type Props = { refreshKey?: number }

export default function RunHistory({ refreshKey = 0 }: Props) {
  const { token } = useAuth()
  const [history, setHistory] = useState<RunEntry[]>([])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (!token) return
    fetch('/api/history', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => (r.ok ? r.json() : []))
      .then((h: RunEntry[]) => setHistory(Array.isArray(h) ? h : []))
      .catch(() => setHistory([]))
  }, [token, refreshKey])

  if (history.length === 0) return null

  return (
    <div className="mt-6">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full rounded-lg border border-white/10 bg-transparent px-3 py-2 text-left font-mono text-xs text-neutral-400"
      >
        {open ? '▾' : '▸'} Previous runs ({history.length})
      </button>
      {open ? (
        <div className="mt-2 flex flex-col gap-1.5">
          {[...history].reverse().map((run, i) => (
            <div
              key={`${run.timestamp}-${i}`}
              className="flex items-center justify-between rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5"
            >
              <div>
                <div className="font-mono text-sm font-medium text-neutral-200">{run.repo}</div>
                <div className="mt-0.5 font-mono text-[11px] text-neutral-500">
                  {new Date(run.timestamp * 1000).toLocaleString()} — {run.label || 'Analysis complete'}
                </div>
              </div>
              <div className="text-right">
                <div className="font-mono text-xl font-bold" style={{ color: riskColor(run.risk_score) }}>
                  {run.risk_score ?? '—'}
                  <span className="text-[11px] font-normal text-neutral-500">/10</span>
                </div>
                <div className="font-mono text-[10px] text-neutral-500">risk</div>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  )
}
