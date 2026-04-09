import { useState } from 'react'
import { Github, Loader2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

type Props = {
  onReady: (repo: string) => void
}

export default function GitHubInput({ onReady }: Props) {
  const { token } = useAuth()
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'done' | 'error'>('idle')
  const [message, setMessage] = useState('')

  const handleFetch = async () => {
    if (!url.trim()) return
    setStatus('loading')
    setMessage('Fetching commits from GitHub...')

    try {
      const r = await fetch('/api/github/fetch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token ?? ''}`,
        },
        body: JSON.stringify({ repo_url: url.trim() }),
      })
      if (!r.ok) {
        const err = (await r.json().catch(() => ({}))) as { detail?: string }
        throw new Error(typeof err.detail === 'string' ? err.detail : 'Fetch failed')
      }
      const data = (await r.json()) as { repo: string; commit_count: number }
      setMessage(`Fetched ${data.commit_count} commits. Applying privacy mask...`)

      const mr = await fetch('/api/mask', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token ?? ''}` },
      })
      if (!mr.ok) {
        const err = (await mr.json().catch(() => ({}))) as { detail?: string }
        throw new Error(typeof err.detail === 'string' ? err.detail : 'Masking failed')
      }

      setStatus('done')
      setMessage(`Ready — ${data.commit_count} commits from ${data.repo}`)
      onReady(data.repo)
    } catch (e) {
      setStatus('error')
      setMessage(e instanceof Error ? e.message : 'Error')
    }
  }

  return (
    <div className="mb-5">
      <label className="mb-2 flex items-center gap-2 font-mono text-[11px] font-semibold uppercase tracking-wider text-neutral-500">
        <Github className="h-3.5 w-3.5 text-neutral-600" />
        GitHub Repository URL
      </label>
      <div className="flex gap-2">
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
          className="input-glow min-w-0 flex-1 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 font-mono text-sm text-neutral-100 transition-all duration-200 placeholder:text-neutral-600"
        />
        <button
          type="button"
          onClick={() => void handleFetch()}
          disabled={status === 'loading' || !url.trim()}
          className="btn-glow flex shrink-0 items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 px-5 py-2.5 font-mono text-sm font-semibold text-white disabled:opacity-40"
        >
          {status === 'loading' ? (
            <>
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Fetching…
            </>
          ) : (
            'Fetch'
          )}
        </button>
      </div>

      {message ? (
        <div
          className={`mt-2.5 rounded-lg border px-3.5 py-2.5 font-mono text-xs ${
            status === 'error'
              ? 'border-red-500/25 bg-red-500/8 text-red-300'
              : status === 'done'
                ? 'border-emerald-500/25 bg-emerald-500/8 text-emerald-300'
                : 'border-indigo-500/25 bg-indigo-500/8 text-indigo-200'
          }`}
        >
          {status === 'loading' ? <span className="mr-1.5 inline-block animate-spin">⟳</span> : null}
          {status === 'done' ? <span className="mr-1.5">✓</span> : null}
          {status === 'error' ? <span className="mr-1.5">✗</span> : null}
          {message}
        </div>
      ) : null}
    </div>
  )
}
