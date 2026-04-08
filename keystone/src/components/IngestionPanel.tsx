import { useCallback, useState } from 'react'
import { motion } from 'framer-motion'
import { FileUp, Sparkles } from 'lucide-react'

type Props = {
  disabled: boolean
  onFile: (file: File) => void
  onAnalyze: () => void
  fileName: string | null
}

export default function IngestionPanel({
  disabled,
  onFile,
  onAnalyze,
  fileName,
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
    <motion.div layout className="relative z-10 mx-auto max-w-3xl px-4">
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDrag(true)
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
        className={`rounded-2xl border-2 border-dashed bg-gradient-active p-[2px] transition-shadow ${
          drag ? 'shadow-glow' : 'shadow-glow-sm'
        }`}
      >
        <label className="flex cursor-pointer flex-col items-center justify-center rounded-2xl bg-black/60 px-8 py-16 backdrop-blur-md transition-colors hover:bg-black/50">
          <FileUp className="mb-4 h-12 w-12 text-indigo-400" strokeWidth={1.25} />
          <span className="font-mono text-lg font-bold tracking-wide text-white">
            UPLOAD REPOSITORY LOGS (.txt)
          </span>
          <span className="mt-2 text-center text-sm text-neutral-500">
            Drop a commit log file here, or click to browse
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
            <span className="mt-4 font-mono text-xs text-emerald-400">{fileName}</span>
          ) : null}
        </label>
      </div>
      <motion.button
        type="button"
        disabled={disabled || !fileName}
        onClick={onAnalyze}
        whileHover={{ scale: disabled || !fileName ? 1 : 1.02 }}
        whileTap={{ scale: disabled || !fileName ? 1 : 0.98 }}
        className="relative mt-8 w-full overflow-hidden rounded-xl border border-indigo-500/40 bg-gradient-to-r from-indigo-600/80 to-violet-600/80 py-4 font-mono text-sm font-bold uppercase tracking-widest text-white shadow-glow disabled:cursor-not-allowed disabled:opacity-40"
      >
        <span className="relative z-10 flex items-center justify-center gap-2">
          <Sparkles className="h-4 w-4" />
          Analyze
        </span>
      </motion.button>
    </motion.div>
  )
}
