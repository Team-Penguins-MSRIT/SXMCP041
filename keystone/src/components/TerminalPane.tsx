import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

type Line = { text: string; kind: 'neutral' | 'success' | 'warn' | 'error' | 'milestone' }

function classifyLine(raw: string): Line['kind'] {
  const s = raw.toUpperCase()
  if (s.includes('PIPELINE COMPLETE')) return 'milestone'
  if (s.includes('CRITICAL ORCHESTRATION')) return 'error'
  if (s.includes('WARN')) return 'warn'
  if (s.includes('FAIL') && s.includes('·')) return 'error'
  if (raw.includes('  ok') && raw.includes('·')) return 'success'
  return 'neutral'
}

const lineCls: Record<Line['kind'], string> = {
  neutral: 'text-neutral-300',
  success: 'text-emerald-400',
  warn: 'text-amber-300',
  error: 'text-red-400',
  milestone: 'text-violet-300 font-semibold',
}

type Props = {
  lines: Line[]
}

export default function TerminalPane({ lines }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [lines])

  return (
    <motion.div
      layout
      className="glass-panel terminal-scroll relative z-10 mx-auto max-w-5xl overflow-hidden"
    >
      <div className="border-b border-white/10 bg-black/40 px-4 py-2 font-mono text-xs text-neutral-500">
        solaris-x · orchestration stream · stdout
      </div>
      <div className="max-h-[min(52vh,520px)] overflow-y-auto bg-black/70 px-4 py-3 font-mono text-[13px] leading-relaxed">
        {lines.length === 0 ? (
          <span className="text-neutral-600">Waiting for pipeline output…</span>
        ) : (
          lines.map((ln, i) => (
            <div key={i} className={`whitespace-pre-wrap ${lineCls[ln.kind]}`}>
              {ln.text}
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </motion.div>
  )
}

export type { Line }
export { classifyLine }
