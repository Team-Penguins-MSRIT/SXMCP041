import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, MessageCircle } from 'lucide-react'

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
      className="glass-panel relative z-10 flex flex-col gap-4 p-5"
    >
      <div className="flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10">
          <MessageCircle className="h-4 w-4 text-emerald-400" />
        </div>
        <div>
          <h3 className="font-mono text-sm font-bold uppercase tracking-wide text-white">
            Actuate &amp; Remediate
          </h3>
          <p className="mt-0.5 text-[11px] text-neutral-600">
            Deploy retention package via WhatsApp bridge
          </p>
        </div>
      </div>

      <input
        type="tel"
        inputMode="numeric"
        autoComplete="tel"
        placeholder="Enter 10-digit mobile number"
        disabled={disabled || loading}
        value={phone}
        onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
        className="input-glow rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 font-mono text-sm text-white transition-all placeholder:text-neutral-600"
      />
      <motion.button
        type="button"
        disabled={disabled || loading || phone.length !== 10}
        onClick={send}
        whileHover={{ scale: phone.length === 10 && !loading ? 1.015 : 1 }}
        className="btn-glow flex items-center justify-center gap-2.5 rounded-xl py-3.5 font-mono text-xs font-bold uppercase tracking-widest text-emerald-300 disabled:cursor-not-allowed disabled:opacity-30"
        style={{
          background: 'linear-gradient(135deg, rgba(16,185,129,0.15), rgba(5,150,105,0.2))',
          border: '1px solid rgba(52,211,153,0.2)',
        }}
      >
        <Send className="h-4 w-4" />
        Send Secure Report
      </motion.button>
      {status ? (
        <p className="rounded-lg border border-emerald-500/20 bg-emerald-500/8 px-3 py-2 font-mono text-xs text-emerald-400/90">
          {status}
        </p>
      ) : null}
    </motion.div>
  )
}
