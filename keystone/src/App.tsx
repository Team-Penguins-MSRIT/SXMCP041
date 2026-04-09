import { useCallback, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Header from './components/Header'
import UserHeader from './components/UserHeader'
import ParticleCanvas from './components/ParticleCanvas'
import IngestionPanel from './components/IngestionPanel'
import TerminalPane, { classifyLine, type Line } from './components/TerminalPane'
import IntelligenceSuite from './components/IntelligenceSuite'
import GitHubInput from './components/GitHubInput'
import RunHistory from './components/RunHistory'
import { useAuth } from './context/AuthContext'
import { consumeSseJson } from './lib/sseFetch'

type Phase = 'idle' | 'processing' | 'results'

type AnalyticsPayload = {
  total_commits: number
  key_person_risk_score?: number | null
  distribution?: { percentage: number }[]
  effective_contributors?: number | null
  risk_level?: string | null
}

export default function App() {
  const { token } = useAuth()
  const [phase, setPhase] = useState<Phase>('idle')
  const [file, setFile] = useState<File | null>(null)
  const [githubReady, setGithubReady] = useState(false)
  const [currentRepo, setCurrentRepo] = useState<string | null>(null)
  const [lines, setLines] = useState<Line[]>([])
  const [pdfFilename, setPdfFilename] = useState<string | null>(null)
  const [busFactorScore, setBusFactorScore] = useState<number | null>(null)
  const [pipelineComplete, setPipelineComplete] = useState(false)
  const [historyTick, setHistoryTick] = useState(0)

  const onFile = useCallback((f: File) => {
    setFile(f)
    setGithubReady(false)
    setCurrentRepo(null)
  }, [])

  const onGithubReady = useCallback((repo: string) => {
    setGithubReady(true)
    setCurrentRepo(repo)
    setFile(null)
  }, [])

  const saveHistory = useCallback(
    async (repoLabel: string, scoreFromDone: number | null | undefined) => {
      if (!token) return
      let analytics: AnalyticsPayload | null = null
      try {
        const r = await fetch('/api/analytics')
        if (r.ok) analytics = (await r.json()) as AnalyticsPayload
      } catch {
        analytics = null
      }
      const topPct = analytics?.distribution?.[0]?.percentage ?? null
      const risk =
        analytics?.key_person_risk_score ?? scoreFromDone ?? null
      await fetch('/api/history/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          repo: repoLabel,
          risk_score: risk,
          top_contributor_pct: topPct,
          effective_contributors: analytics?.effective_contributors,
          label: analytics?.risk_level || 'Analysis complete',
        }),
      })
        .then(() => setHistoryTick((t) => t + 1))
        .catch(() => {})
    },
    [token],
  )

  const runPipeline = useCallback(async () => {
    if (!file && !githubReady) return
    setLines([])
    setPdfFilename(null)
    setBusFactorScore(null)
    setPipelineComplete(false)
    setPhase('processing')

    try {
      if (file) {
        const fd = new FormData()
        fd.append('file', file)
        const up = await fetch('/api/upload', { method: 'POST', body: fd })
        if (!up.ok) {
          const err = (await up.json().catch(() => ({}))) as { detail?: string }
          setLines([
            {
              text: `Upload failed: ${typeof err.detail === 'string' ? err.detail : up.status}`,
              kind: 'error',
            },
          ])
          setPhase('idle')
          return
        }
      }

      const mask = await fetch('/api/mask', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token ?? ''}` },
      })
      if (!mask.ok) {
        const err = (await mask.json().catch(() => ({}))) as { detail?: string }
        setLines([
          {
            text: `Mask step failed: ${typeof err.detail === 'string' ? err.detail : mask.status}`,
            kind: 'error',
          },
        ])
        setPhase('idle')
        return
      }

      let finished = false
      await consumeSseJson('/api/run/stream', {}, (msg: unknown) => {
        const m = msg as {
          type: string
          clean?: string
          pdf_filename?: string
          bus_factor_score?: number | null
          complete?: boolean
          milestone?: string
        }
        if (m.type === 'line' && m.clean != null) {
          setLines((prev) => [...prev, { text: m.clean!, kind: classifyLine(m.clean!) }])
          if (m.milestone === 'pipeline_complete' || m.clean.includes('PIPELINE COMPLETE')) {
            setPipelineComplete(true)
          }
        }
        if (m.type === 'done') {
          finished = true
          if (m.pdf_filename) setPdfFilename(m.pdf_filename)
          if (m.bus_factor_score != null) setBusFactorScore(m.bus_factor_score)
          if (m.complete) setPipelineComplete(true)
          const repoLabel = currentRepo ?? file?.name ?? 'Uploaded file'
          void saveHistory(repoLabel, m.bus_factor_score)
          setPhase('results')
        }
      })

      if (!finished) {
        setLines((prev) => [
          ...prev,
          { text: 'Stream ended without completion event.', kind: 'error' },
        ])
        setPhase((p) => (p === 'processing' ? 'idle' : p))
      }
    } catch (e) {
      setLines((prev) => [
        ...prev,
        {
          text: `Pipeline error: ${e instanceof Error ? e.message : String(e)}`,
          kind: 'error',
        },
      ])
      setPhase((p) => (p === 'processing' ? 'idle' : p))
    }
  }, [file, githubReady, currentRepo, token, saveHistory])

  const canAnalyze = Boolean(file) || githubReady

  return (
    <div className="relative min-h-full overflow-x-hidden">
      <ParticleCanvas />
      <div className="relative z-[1] min-h-full">
        <UserHeader />
        <Header />
        <AnimatePresence mode="wait">
          {phase === 'idle' && (
            <motion.section
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="py-16"
            >
              <div className="relative z-10 mx-auto max-w-3xl px-4">
                <GitHubInput onReady={onGithubReady} />
                <IngestionPanel
                  disabled={false}
                  fileName={file?.name ?? null}
                  onFile={onFile}
                  onAnalyze={runPipeline}
                  analyzeDisabled={!canAnalyze}
                />
                <RunHistory refreshKey={historyTick} />
              </div>
            </motion.section>
          )}
          {phase === 'processing' && (
            <motion.section
              key="proc"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="space-y-6 py-10"
            >
              <TerminalPane lines={lines} />
            </motion.section>
          )}
          {phase === 'results' && (
            <motion.section
              key="results"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <TerminalPane lines={lines} />
              <IntelligenceSuite
                pdfFilename={pdfFilename}
                pipelineComplete={pipelineComplete}
                busFactorScore={busFactorScore}
              />
            </motion.section>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
