import { motion } from 'framer-motion'

export default function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative z-10 border-b border-white/10 bg-black/30 px-6 py-5 backdrop-blur-md"
    >
      <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white md:text-3xl">
        THE KEYSTONE
      </h1>
      <p className="mt-1 max-w-xl font-sans text-sm text-neutral-400">
        Operational Intelligence. Mitigating M&amp;A Risk.
      </p>
    </motion.header>
  )
}
