import { motion } from 'framer-motion'
import { FileText } from 'lucide-react'
import QuantitativeRiskDashboard from './QuantitativeRiskDashboard'
import ActuatePanel from './ActuatePanel'
import MaskMapViewer from './MaskMapViewer'

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
      className="relative z-10 mx-auto grid max-w-[1600px] gap-5 px-4 pb-16 pt-4 md:grid-cols-2"
    >
      <motion.div
        layout
        className="glass-panel flex min-h-[520px] flex-col overflow-hidden md:min-h-[72vh]"
      >
        <div className="flex shrink-0 items-center gap-2 border-b border-white/[0.06] bg-black/30 px-4 py-2.5">
          <FileText className="h-3.5 w-3.5 text-indigo-400" />
          <span className="font-mono text-xs font-medium text-neutral-500">
            KeyStone Report · PDF
          </span>
          {pdfFilename ? (
            <span className="ml-1 rounded bg-white/5 px-2 py-0.5 font-mono text-[10px] text-neutral-500">
              {pdfFilename}
            </span>
          ) : null}
        </div>
        <div className="relative min-h-0 w-full flex-1 bg-[#080810]/80">
          <iframe
            title="Due diligence PDF"
            src={`${pdfSrc}#toolbar=1`}
            className="h-full min-h-[480px] w-full rounded-md border-0 md:min-h-0"
          />
        </div>
      </motion.div>
      <div className="flex flex-col gap-4">
        <QuantitativeRiskDashboard busFactorScore={busFactorScore} />
        <MaskMapViewer />
        <ActuatePanel disabled={!pipelineComplete} />
      </div>
    </motion.div>
  )
}
