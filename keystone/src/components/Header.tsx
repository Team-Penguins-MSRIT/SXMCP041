import { motion } from 'framer-motion'
import { Shield } from 'lucide-react'

export default function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative z-10 border-b border-white/[0.06] bg-black/40 px-6 py-5 backdrop-blur-xl"
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 shadow-lg shadow-indigo-500/20">
              <Shield className="h-5 w-5 text-white" strokeWidth={2.5} />
            </div>
            <h1 className="text-shimmer font-mono text-2xl font-extrabold tracking-tight md:text-3xl">
              THE KEYSTONE
            </h1>
          </div>
          <p className="mt-1.5 max-w-xl pl-12 font-sans text-[13px] text-neutral-500">
            Operational Intelligence · Mitigating M&amp;A Key-Person Risk
          </p>
        </div>
        <div className="hidden items-center gap-3 sm:flex">
          <div className="flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1">
            <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            <span className="font-mono text-[10px] font-medium text-emerald-400">
              System Online
            </span>
          </div>
        </div>
      </div>
    </motion.header>
  )
}
