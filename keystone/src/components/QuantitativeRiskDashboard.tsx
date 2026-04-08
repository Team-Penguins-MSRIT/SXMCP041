import { useEffect, useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Activity, GitCommit, Users } from 'lucide-react'

export type AnalyticsDistribution = {
  author: string
  count: number
  percentage: number
}

export type AnalyticsPayload = {
  total_commits: number
  unique_contributors: number
  distribution: AnalyticsDistribution[]
  key_person_risk_score?: number | null
  concentration_hhi?: number | null
  effective_contributors?: number | null
  contributors_50pct?: number | null
  contributors_90pct?: number | null
  concentration_index?: number | null
  risk_level?: string | null
  top_share?: number | null
  repository_bus_factor_breadth?: number | null
}

type Props = {
  busFactorScore?: number | null
}

function barColorClass(pct: number): string {
  if (pct >= 50) return 'bg-red-500'
  if (pct >= 30) return 'bg-yellow-500'
  return 'bg-emerald-500'
}

export default function QuantitativeRiskDashboard({ busFactorScore }: Props) {
  const [data, setData] = useState<AnalyticsPayload | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    fetch('/api/analytics')
      .then((res) => {
        if (!res.ok) {
          return res.json().then((j) => {
            throw new Error(typeof j.detail === 'string' ? j.detail : res.statusText)
          })
        }
        return res.json()
      })
      .then((json: unknown) => {
        if (!cancelled) setData(json as AnalyticsPayload)
      })
      .catch((e: Error) => {
        if (!cancelled) {
          setError(e.message)
          setData(null)
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const topShare = data?.distribution?.[0]?.percentage ?? 0
  const isCritical = topShare >= 50

  const displayRiskScore = useMemo(() => {
    if (data && data.total_commits > 0 && data.key_person_risk_score != null) {
      return data.key_person_risk_score
    }
    if (busFactorScore != null) return busFactorScore
    return null
  }, [data, busFactorScore])

  return (
    <div className="glass-panel flex flex-col gap-4 p-4">
      <div className="border-b border-white/10 pb-2 font-mono text-xs font-bold uppercase tracking-widest text-indigo-300">
        Quantitative risk analysis
      </div>

      {loading ? (
        <p className="font-mono text-sm text-neutral-500">Loading analytics…</p>
      ) : error ? (
        <p className="font-mono text-sm text-red-400">{error}</p>
      ) : !data ? null : (
        <>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3"
            >
              <div className="flex items-center gap-2 text-neutral-500">
                <Activity className="h-4 w-4 text-violet-400" />
                <span className="font-mono text-[10px] uppercase tracking-wide">
                  Consolidated risk (1–10)
                </span>
              </div>
              <p className="mt-1 font-mono text-2xl font-bold text-white">
                {displayRiskScore != null ? String(displayRiskScore) : '—'}
                {displayRiskScore != null ? (
                  <span className="text-sm font-normal text-neutral-500"> /10</span>
                ) : null}
              </p>
              {data.effective_contributors != null && data.concentration_hhi != null ? (
                <p className="mt-1 font-mono text-[10px] leading-snug text-neutral-500">
                  1/HHI ≈ {data.effective_contributors} · HHI {data.concentration_hhi}
                  {data.contributors_90pct != null
                    ? ` · Bus factor breadth (90%): ${data.contributors_90pct} (higher is safer)`
                    : ''}
                </p>
              ) : null}
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3"
            >
              <div className="flex items-center gap-2 text-neutral-500">
                <GitCommit className="h-4 w-4 text-cyan-400" />
                <span className="font-mono text-[10px] uppercase tracking-wide">Total commits</span>
              </div>
              <p className="mt-1 font-mono text-2xl font-bold text-white">{data.total_commits}</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3"
            >
              <div className="flex items-center gap-2 text-neutral-500">
                <Users className="h-4 w-4 text-emerald-400" />
                <span className="font-mono text-[10px] uppercase tracking-wide">Contributors</span>
              </div>
              <p className="mt-1 font-mono text-2xl font-bold text-white">{data.unique_contributors}</p>
            </motion.div>
          </div>

          <div>
            <h3 className="mb-3 font-mono text-xs font-semibold uppercase tracking-wide text-neutral-400">
              Ownership distribution
            </h3>
            <div className="flex max-h-[min(42vh,360px)] flex-col gap-2.5 overflow-y-auto pr-1">
              {data.distribution.map((row) => (
                <div key={row.author} className="space-y-1">
                  <div className="flex justify-between gap-2 font-mono text-[11px] text-neutral-300">
                    <span className="min-w-0 truncate" title={row.author}>
                      {row.author}
                    </span>
                    <span className="shrink-0 text-neutral-500">
                      {row.count} · {row.percentage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-white/5">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${barColorClass(row.percentage)}`}
                      style={{ width: `${row.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {data.distribution.length > 0 ? (
            isCritical ? (
              <div className="rounded-xl border border-red-500/40 bg-red-950/40 px-4 py-3 font-mono text-sm leading-relaxed text-red-200">
                <span className="text-red-400">⚠️ CRITICAL:</span> Codebase ownership is severely
                concentrated. High Key-Person Risk.
              </div>
            ) : (
              <div className="rounded-xl border border-emerald-500/35 bg-emerald-950/30 px-4 py-3 font-mono text-sm leading-relaxed text-emerald-100">
                <span className="text-emerald-400">✅ HEALTHY:</span> Codebase ownership is well
                distributed. Low Key-Person Risk.
              </div>
            )
          ) : null}
        </>
      )}
    </div>
  )
}
