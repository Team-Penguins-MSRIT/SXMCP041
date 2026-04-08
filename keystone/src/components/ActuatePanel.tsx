import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send } from 'lucide-react'

type Props = {
  disabled?: boolean
}

export default function ActuatePanel({ disabled }: Props) {
  const [phone, setPhone] = useState('')
  const [status, setStatus] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function send() {
    setStatus(null)
    setLoading(true)
    try {
      const res = await fetch('/api/actuate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: phone.trim() }),
      })
      const body = await res.json().catch(() => ({}))
      if (!res.ok) {
        const d = body.detail
        const msg =
          typeof d === 'string'
            ? d
            : Array.isArray(d)
              ? d.map((x: { msg?: string }) => x.msg).filter(Boolean).join('; ')
              : 'Delivery failed'
        setStatus(msg)
        return
      }
      setStatus('Secure report dispatched via WhatsApp bridge.')
    } catch {
      setStatus('Network error calling API')
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      layout
      className="glass-panel relative z-10 flex flex-col gap-3 p-4"
    >
      <h3 className="font-mono text-sm font-bold uppercase tracking-wide text-white">
        Actuate &amp; Remediate
      </h3>
      <p className="text-xs text-neutral-500">
        Deploy retention package — PDF is sent through the local WhatsApp bridge (91 prefix
        applied server-side).
      </p>
      <input
        type="tel"
        inputMode="numeric"
        autoComplete="tel"
        placeholder="Enter 10-digit mobile number"
        disabled={disabled || loading}
        value={phone}
        onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
        className="rounded-lg border border-white/10 bg-black/50 px-3 py-2.5 font-mono text-sm text-white placeholder:text-neutral-600 focus:border-indigo-500/50 focus:outline-none focus:ring-1 focus:ring-indigo-500/40"
      />
      <motion.button
        type="button"
        disabled={disabled || loading || phone.length !== 10}
        onClick={send}
        whileHover={{ scale: phone.length === 10 && !loading ? 1.02 : 1 }}
        className="flex items-center justify-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-900/30 py-3 font-mono text-xs font-bold uppercase tracking-widest text-emerald-300 disabled:cursor-not-allowed disabled:opacity-40"
      >
        <Send className="h-4 w-4" />
        Send secure report
      </motion.button>
      {status ? (
        <p className="font-mono text-xs text-emerald-400/90">{status}</p>
      ) : null}
    </motion.div>
  )
}
