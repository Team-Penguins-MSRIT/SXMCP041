import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Terminal } from 'lucide-react'

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
  neutral: 'text-neutral-400',
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
      <div className="flex items-center gap-2.5 border-b border-white/[0.06] bg-black/50 px-4 py-2.5">
        <div className="flex gap-1.5">
          <div className="h-2.5 w-2.5 rounded-full bg-red-500/60" />
          <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/60" />
          <div className="h-2.5 w-2.5 rounded-full bg-emerald-500/60" />
        </div>
        <div className="flex items-center gap-1.5 font-mono text-[11px] text-neutral-600">
          <Terminal className="h-3 w-3" />
          keystone · orchestration stream · stdout
        </div>
      </div>
      <div className="max-h-[min(52vh,520px)] overflow-y-auto bg-[#080810]/80 px-4 py-3 font-mono text-[13px] leading-relaxed">
        {lines.length === 0 ? (
          <span className="text-neutral-600">
            <span className="mr-1 animate-pulse text-indigo-500">▎</span>
            Waiting for pipeline output…
          </span>
        ) : (
          lines.map((ln, i) => (
            <div key={i} className={`whitespace-pre-wrap ${lineCls[ln.kind]}`}>
              <span className="mr-2 select-none text-neutral-700">{String(i + 1).padStart(3, ' ')}</span>
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
