import { motion } from 'framer-motion'
import QuantitativeRiskDashboard from './QuantitativeRiskDashboard'
import ActuatePanel from './ActuatePanel'

type Props = {
  pdfFilename: string | null
  pipelineComplete: boolean
  busFactorScore?: number | null
}

export default function IntelligenceSuite({
  pdfFilename,
  pipelineComplete,
  busFactorScore,
}: Props) {
  const pdfSrc = pdfFilename
    ? `/api/pdf/${encodeURIComponent(pdfFilename)}`
    : '/api/pdf/latest'

  return (
    <motion.div
      layout
      className="relative z-10 mx-auto grid max-w-[1600px] gap-4 px-4 pb-16 pt-4 md:grid-cols-2"
    >
      <motion.div
        layout
        className="glass-panel flex min-h-[520px] flex-col overflow-hidden md:min-h-[72vh]"
      >
        <div className="shrink-0 border-b border-white/10 px-4 py-2 font-mono text-xs text-neutral-500">
          Bus factor report · PDF
          {pdfFilename ? (
            <span className="ml-2 text-neutral-400">({pdfFilename})</span>
          ) : null}
        </div>
        <div className="relative min-h-0 w-full flex-1 bg-neutral-950/80">
          <iframe
            title="Due diligence PDF"
            src={`${pdfSrc}#toolbar=1`}
            className="h-full min-h-[480px] w-full rounded-md border-0 md:min-h-0"
          />
        </div>
      </motion.div>
      <div className="flex flex-col gap-4">
        <QuantitativeRiskDashboard busFactorScore={busFactorScore} />
        <ActuatePanel disabled={!pipelineComplete} />
      </div>
    </motion.div>
  )
}
