import { useCallback, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Header from './components/Header'
import ParticleCanvas from './components/ParticleCanvas'
import IngestionPanel from './components/IngestionPanel'
import TerminalPane, { classifyLine, type Line } from './components/TerminalPane'
import IntelligenceSuite from './components/IntelligenceSuite'

type Phase = 'idle' | 'processing' | 'results'

export default function App() {
  const [phase, setPhase] = useState<Phase>('idle')
  const [file, setFile] = useState<File | null>(null)
  const [lines, setLines] = useState<Line[]>([])
  const [pdfFilename, setPdfFilename] = useState<string | null>(null)
  const [busFactorScore, setBusFactorScore] = useState<number | null>(null)
  const [pipelineComplete, setPipelineComplete] = useState(false)

  const onFile = useCallback((f: File) => {
    setFile(f)
  }, [])

  const runPipeline = useCallback(async () => {
    if (!file) return
    setLines([])
    setPdfFilename(null)
    setBusFactorScore(null)
    setPipelineComplete(false)
    setPhase('processing')

    const fd = new FormData()
    fd.append('file', file)
    const up = await fetch('/api/upload', { method: 'POST', body: fd })
    if (!up.ok) {
      const err = await up.json().catch(() => ({}))
      setLines([
        {
          text: `Upload failed: ${typeof err.detail === 'string' ? err.detail : up.status}`,
          kind: 'error',
        },
      ])
      setPhase('idle')
      return
    }

    const es = new EventSource('/api/run/stream')
    let finished = false

    es.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data) as {
          type: string
          clean?: string
          pdf_filename?: string
          bus_factor_score?: number | null
          complete?: boolean
          milestone?: string
        }
        if (msg.type === 'line' && msg.clean != null) {
          setLines((prev) => [
            ...prev,
            { text: msg.clean!, kind: classifyLine(msg.clean!) },
          ])
          if (msg.milestone === 'pipeline_complete' || msg.clean.includes('PIPELINE COMPLETE')) {
            setPipelineComplete(true)
          }
        }
        if (msg.type === 'done') {
          finished = true
          if (msg.pdf_filename) setPdfFilename(msg.pdf_filename)
          if (msg.bus_factor_score != null) setBusFactorScore(msg.bus_factor_score)
          if (msg.complete) setPipelineComplete(true)
          es.close()
          setPhase('results')
        }
      } catch {
        /* ignore parse */
      }
    }

    es.onerror = () => {
      if (finished) return
      es.close()
      setLines((prev) => [
        ...prev,
        { text: 'EventSource error — check FastAPI (api.py) and MCP stack.', kind: 'error' },
      ])
      setPhase((p) => (p === 'processing' ? 'idle' : p))
    }
  }, [file])

  return (
    <div className="relative min-h-full overflow-x-hidden">
      <ParticleCanvas />
      <div className="relative z-[1] min-h-full">
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
              <IngestionPanel
                disabled={false}
                fileName={file?.name ?? null}
                onFile={onFile}
                onAnalyze={runPipeline}
              />
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
