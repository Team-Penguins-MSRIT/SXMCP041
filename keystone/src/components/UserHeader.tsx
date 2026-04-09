import { LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const ROLE_COLORS: Record<string, { bg: string; border: string; color: string; label: string }> = {
  ceo: { bg: 'rgba(251,191,36,0.12)', border: 'rgba(251,191,36,0.25)', color: '#fbbf24', label: 'CEO' },
  pm: { bg: 'rgba(139,92,246,0.12)', border: 'rgba(139,92,246,0.25)', color: '#a78bfa', label: 'PM' },
  dev: { bg: 'rgba(52,211,153,0.12)', border: 'rgba(52,211,153,0.25)', color: '#34d399', label: 'DEV' },
}

export default function UserHeader() {
  const { user, logout } = useAuth()
  if (!user) return null

  const badge = ROLE_COLORS[user.role] ?? {
    bg: 'rgba(156,163,175,0.12)',
    border: 'rgba(156,163,175,0.25)',
    color: '#9ca3af',
    label: user.role?.toUpperCase() || 'USER',
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '8px 20px',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        background: 'linear-gradient(90deg, rgba(99,102,241,0.04) 0%, rgba(0,0,0,0.5) 50%, rgba(139,92,246,0.04) 100%)',
        backdropFilter: 'blur(16px)',
        fontFamily: "'JetBrains Mono', ui-monospace, monospace",
        fontSize: 12,
        position: 'relative',
        zIndex: 50,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{
          background: 'linear-gradient(135deg, #6366f1, #a78bfa)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: 800,
          fontSize: 13,
          letterSpacing: '0.02em',
        }}>
          KeyStone
        </span>
        <span style={{ color: 'rgba(255,255,255,0.1)' }}>·</span>
        <span style={{ color: '#6b7280', fontSize: 11 }}>{user.org}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span
          style={{
            padding: '2px 10px',
            borderRadius: 6,
            fontSize: 10,
            fontWeight: 700,
            background: badge.bg,
            border: `1px solid ${badge.border}`,
            color: badge.color,
            letterSpacing: '0.1em',
          }}
        >
          {badge.label}
        </span>
        <span style={{ color: '#d1d5db', fontWeight: 500 }}>{user.name}</span>
        <button
          type="button"
          onClick={logout}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            padding: '5px 12px',
            background: 'rgba(239,68,68,0.08)',
            border: '1px solid rgba(239,68,68,0.15)',
            borderRadius: 8,
            color: '#f87171',
            fontSize: 11,
            fontWeight: 600,
            cursor: 'pointer',
            fontFamily: 'inherit',
            pointerEvents: 'all',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(239,68,68,0.15)'
            e.currentTarget.style.borderColor = 'rgba(239,68,68,0.3)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(239,68,68,0.08)'
            e.currentTarget.style.borderColor = 'rgba(239,68,68,0.15)'
          }}
        >
          <LogOut size={12} />
          Sign out
        </button>
      </div>
    </div>
  )
}
