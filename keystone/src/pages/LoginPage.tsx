import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

const DEMO_ACCOUNTS = [
  { role: 'CEO', email: 'ceo@keystone.ai', label: 'Full transparency' },
  { role: 'PM', email: 'pm1@keystone.ai', label: 'Masked contributors' },
  { role: 'Dev', email: 'dev@keystone.ai', label: 'Own data only' },
]

export default function LoginPage() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [enterprise, setEnterprise] = useState('')
  const [designation, setDesignation] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setSuccess(false)
    await login(email, password, { enterprise, designation })
    setSuccess(true)
    await new Promise((r) => setTimeout(r, 800))
    setLoading(false)
  }

  const quickLogin = (demoEmail: string) => {
    setEmail(demoEmail)
    setPassword('demo123')
    setEnterprise('KeyStone')
    setDesignation(
      demoEmail.includes('ceo')
        ? 'Chief Executive Officer'
        : demoEmail.includes('pm')
          ? 'Project Manager'
          : 'Developer',
    )
  }

  return (
    <div className="bg-mesh dot-grid relative flex min-h-screen items-center justify-center overflow-hidden bg-[#050509]">
      {/* Decorative orbs */}
      <div
        className="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full opacity-30 blur-[120px]"
        style={{ background: 'radial-gradient(circle, #6366f1 0%, transparent 70%)' }}
      />
      <div
        className="pointer-events-none absolute -bottom-48 -right-32 h-[500px] w-[500px] rounded-full opacity-20 blur-[120px]"
        style={{ background: 'radial-gradient(circle, #7c3aed 0%, transparent 70%)' }}
      />

      <div className="relative z-10 w-full max-w-[440px] px-6">
        {/* Brand */}
        <div className="mb-10 text-center">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/10 px-4 py-1.5">
            <div className="h-2 w-2 animate-pulse rounded-full bg-indigo-400" />
            <span className="font-mono text-[10px] font-semibold uppercase tracking-[0.25em] text-indigo-300">
              Secure Access
            </span>
          </div>
          <h1 className="text-shimmer font-mono text-4xl font-extrabold tracking-tight">
            KeyStone
          </h1>
          <p className="mt-2 font-sans text-sm text-neutral-500">
            Key-person risk intelligence platform
          </p>
        </div>

        {/* Form Card */}
        <div className="animated-border glow-pulse">
          <form
            onSubmit={handleSubmit}
            className="relative rounded-2xl border border-white/[0.06] bg-[#0c0c14]/90 p-7 backdrop-blur-xl"
          >
            {/* Two-column: Email + Password */}
            <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block font-mono text-[10px] font-semibold uppercase tracking-wider text-neutral-500">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="you@company.ai"
                  className="input-glow w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5 font-mono text-sm text-neutral-100 transition-all duration-200 placeholder:text-neutral-600"
                />
              </div>
              <div>
                <label className="mb-1.5 block font-mono text-[10px] font-semibold uppercase tracking-wider text-neutral-500">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="input-glow w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5 font-mono text-sm text-neutral-100 transition-all duration-200 placeholder:text-neutral-600"
                />
              </div>
            </div>

            {/* Two-column: Enterprise + Designation */}
            <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block font-mono text-[10px] font-semibold uppercase tracking-wider text-neutral-500">
                  Enterprise
                </label>
                <input
                  type="text"
                  value={enterprise}
                  onChange={(e) => setEnterprise(e.target.value)}
                  required
                  placeholder="Acme Corp"
                  className="input-glow w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5 font-mono text-sm text-neutral-100 transition-all duration-200 placeholder:text-neutral-600"
                />
              </div>
              <div>
                <label className="mb-1.5 block font-mono text-[10px] font-semibold uppercase tracking-wider text-neutral-500">
                  Designation
                </label>
                <input
                  type="text"
                  value={designation}
                  onChange={(e) => setDesignation(e.target.value)}
                  required
                  placeholder="VP of Engineering"
                  className="input-glow w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5 font-mono text-sm text-neutral-100 transition-all duration-200 placeholder:text-neutral-600"
                />
              </div>
            </div>

            {/* Success banner */}
            {success && (
              <div className="mb-4 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-2.5 text-center">
                <span className="font-mono text-xs font-semibold text-emerald-300">
                  ✓ Authentication successful — launching dashboard…
                </span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-glow group relative w-full overflow-hidden rounded-xl py-3.5 font-mono text-sm font-bold uppercase tracking-widest text-white transition-all disabled:cursor-not-allowed disabled:opacity-50"
              style={{
                background: success
                  ? 'linear-gradient(135deg, #059669, #10b981)'
                  : 'linear-gradient(135deg, #4f46e5, #7c3aed)',
              }}
            >
              <span className="relative z-10">
                {success
                  ? '✓ Authenticated'
                  : loading
                    ? 'Verifying credentials…'
                    : 'Sign In →'}
              </span>
              {/* Button shimmer effect */}
              {!loading && !success && (
                <div
                  className="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
                  style={{
                    background:
                      'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%, rgba(255,255,255,0.05) 100%)',
                  }}
                />
              )}
            </button>
          </form>
        </div>

        {/* Demo accounts */}
        <div className="mt-5 rounded-xl border border-indigo-500/15 bg-indigo-500/[0.04] p-4 backdrop-blur-sm">
          <div className="mb-3 flex items-center gap-2">
            <div className="h-px flex-1 bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent" />
            <span className="font-mono text-[9px] font-semibold uppercase tracking-[0.2em] text-indigo-400/70">
              Demo Accounts · demo123
            </span>
            <div className="h-px flex-1 bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent" />
          </div>
          <div className="space-y-1.5">
            {DEMO_ACCOUNTS.map((a) => (
              <button
                key={a.email}
                type="button"
                onClick={() => quickLogin(a.email)}
                className="group flex w-full items-center justify-between rounded-lg border border-white/[0.05] bg-white/[0.02] px-3 py-2.5 text-left font-mono transition-all duration-200 hover:border-indigo-500/30 hover:bg-indigo-500/[0.06]"
              >
                <div className="flex items-center gap-2.5">
                  <span className="inline-flex h-6 min-w-[42px] items-center justify-center rounded-md bg-indigo-500/15 px-2 text-[10px] font-bold text-indigo-300">
                    {a.role}
                  </span>
                  <span className="text-xs text-neutral-400 transition-colors group-hover:text-neutral-200">
                    {a.email}
                  </span>
                </div>
                <span className="text-[10px] text-neutral-600 transition-colors group-hover:text-neutral-400">
                  {a.label}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Footer */}
        <p className="mt-6 text-center font-mono text-[10px] text-neutral-600">
          KeyStone v1.0 · Encrypted session · Zero-trust architecture
        </p>
      </div>
    </div>
  )
}
