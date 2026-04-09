import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'

export default function MaskMapViewer() {
  const { user, token } = useAuth()
  const [map, setMap] = useState<Record<string, string>>({})

  useEffect(() => {
    if (user?.role !== 'ceo' || !token) return
    fetch('/api/mask/map', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => (r.ok ? r.json() : {}))
      .then((d: Record<string, string>) => setMap(d && typeof d === 'object' ? d : {}))
      .catch(() => setMap({}))
  }, [user, token])

  if (user?.role !== 'ceo') return null
  const entries = Object.entries(map)
  if (entries.length === 0) return null

  return (
    <div className="mt-4 rounded-xl border border-indigo-500/20 bg-indigo-500/[0.06] px-4 py-3">
      <div className="mb-2 font-mono text-[10px] font-semibold uppercase tracking-widest text-indigo-300">
        Identity map — CEO only
      </div>
      <div className="grid grid-cols-1 gap-1 sm:grid-cols-2">
        {entries.map(([real, alias]) => (
          <div
            key={alias}
            className="flex justify-between border-b border-white/5 py-1 font-mono text-xs last:border-0"
          >
            <span className="font-semibold text-indigo-300">{alias}</span>
            <span className="text-neutral-300">{real}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
