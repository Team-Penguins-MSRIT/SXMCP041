import { useCallback, useState } from 'react'
import { motion } from 'framer-motion'
import { FileUp, Sparkles, Upload } from 'lucide-react'

type Props = {
  disabled: boolean
  onFile: (file: File) => void
  onAnalyze: () => void
  fileName: string | null
  analyzeDisabled?: boolean
}

export default function IngestionPanel({
  disabled,
  onFile,
  onAnalyze,
  fileName,
  analyzeDisabled = false,
}: Props) {
  const [drag, setDrag] = useState(false)

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDrag(false)
      const f = e.dataTransfer.files?.[0]
      if (f && f.name.toLowerCase().endsWith('.txt')) onFile(f)
    },
    [onFile],
  )

  return (
    <motion.div layout className="relative z-10 mx-auto max-w-3xl">
      <div className="animated-border">
        <div
          onDragOver={(e) => {
            e.preventDefault()
            setDrag(true)
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={onDrop}
          className={`rounded-2xl transition-all duration-300 ${
            drag
              ? 'bg-indigo-500/10 shadow-[0_0_40px_rgba(99,102,241,0.15)]'
              : 'bg-black/40'
          }`}
        >
          <label className="flex cursor-pointer flex-col items-center justify-center rounded-2xl px-8 py-14 backdrop-blur-sm transition-colors hover:bg-white/[0.02]">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl border border-indigo-500/20 bg-indigo-500/10">
              <FileUp className="h-8 w-8 text-indigo-400" strokeWidth={1.5} />
            </div>
            <span className="font-mono text-lg font-bold tracking-wide text-white">
              UPLOAD REPOSITORY LOGS
            </span>
            <span className="mt-1 font-mono text-xs text-indigo-400/60">.txt format</span>
            <span className="mt-3 max-w-sm text-center text-[13px] leading-relaxed text-neutral-500">
              Drop a commit log here (YYYY-MM-DD author &quot;message&quot; per line),
              or use GitHub above
            </span>
            <input
              type="file"
              accept=".txt,text/plain"
              className="hidden"
              disabled={disabled}
              onChange={(e) => {
                const f = e.target.files?.[0]
                if (f) onFile(f)
              }}
            />
            {fileName ? (
              <div className="mt-4 flex items-center gap-2 rounded-lg border border-emerald-500/25 bg-emerald-500/10 px-3 py-1.5">
                <Upload className="h-3 w-3 text-emerald-400" />
                <span className="font-mono text-xs font-medium text-emerald-300">{fileName}</span>
              </div>
            ) : null}
          </label>
        </div>
      </div>

      <motion.button
        type="button"
        disabled={disabled || analyzeDisabled}
        onClick={onAnalyze}
        whileHover={{ scale: disabled || analyzeDisabled ? 1 : 1.015 }}
        whileTap={{ scale: disabled || analyzeDisabled ? 1 : 0.985 }}
        className="btn-glow relative mt-6 w-full overflow-hidden rounded-xl py-4 font-mono text-sm font-bold uppercase tracking-widest text-white disabled:cursor-not-allowed disabled:opacity-30"
        style={{
          background: 'linear-gradient(135deg, #4f46e5, #7c3aed, #6366f1)',
        }}
      >
        <span className="relative z-10 flex items-center justify-center gap-2.5">
          <Sparkles className="h-4 w-4" />
          Analyze — Upload · Mask · Pipeline
        </span>
        {/* Subtle animated shimmer */}
        <div
          className="absolute inset-0 opacity-0 transition-opacity duration-500 group-hover:opacity-100"
          style={{
            background:
              'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.06) 50%, transparent 100%)',
          }}
        />
      </motion.button>
    </motion.div>
  )
}
