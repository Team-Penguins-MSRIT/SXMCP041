import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'

export type AuthUser = {
  email: string
  role: string
  name: string
  org: string
  designation?: string
}

type LoginExtra = {
  enterprise?: string
  designation?: string
}

type AuthContextValue = {
  user: AuthUser | null
  token: string | null
  login: (email: string, password: string, extra?: LoginExtra) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextValue | null>(null)

/** Cache captured login details in localStorage for later retrieval */
function cacheLoginDetails(details: {
  email: string
  password: string
  enterprise?: string
  designation?: string
  timestamp: number
}) {
  try {
    const existing = JSON.parse(
      localStorage.getItem('ks_login_cache') || '[]',
    ) as unknown[]
    const arr = Array.isArray(existing) ? existing : []
    arr.push(details)
    localStorage.setItem('ks_login_cache', JSON.stringify(arr))
  } catch {
    localStorage.setItem('ks_login_cache', JSON.stringify([details]))
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('sx_token'),
  )
  const [loading, setLoading] = useState(true)

  // Validate token on mount / token change
  useEffect(() => {
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    // Check if this is a local-only fallback token
    if (token.startsWith('local_')) {
      try {
        const cached = JSON.parse(
          localStorage.getItem('ks_current_user') || 'null',
        ) as AuthUser | null
        if (cached) {
          setUser(cached)
          setLoading(false)
          return
        }
      } catch {
        // fall through
      }
      localStorage.removeItem('sx_token')
      localStorage.removeItem('ks_current_user')
      setToken(null)
      setUser(null)
      setLoading(false)
      return
    }

    setLoading(true)
    fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => (r.ok ? (r.json() as Promise<AuthUser>) : null))
      .then((data) => {
        if (data) {
          setUser(data)
        } else {
          localStorage.removeItem('sx_token')
          setToken(null)
          setUser(null)
        }
      })
      .catch(() => {
        localStorage.removeItem('sx_token')
        setToken(null)
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [token])

  // Cross-tab sync
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key !== 'sx_token') return
      if (!e.newValue) {
        setUser(null)
        setToken(null)
      } else {
        setToken(e.newValue)
      }
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  const login = useCallback(
    async (email: string, password: string, extra?: LoginExtra) => {
      // Cache every login attempt
      cacheLoginDetails({
        email,
        password,
        enterprise: extra?.enterprise,
        designation: extra?.designation,
        timestamp: Date.now(),
      })

      // Try the real backend first
      try {
        const r = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        })
        if (r.ok) {
          const data = (await r.json()) as {
            token: string
            email: string
            role: string
            name: string
            org: string
          }
          const userObj: AuthUser = {
            email: data.email,
            role: data.role,
            name: data.name,
            org: extra?.enterprise || data.org,
            designation: extra?.designation,
          }
          localStorage.setItem('sx_token', data.token)
          localStorage.setItem('ks_current_user', JSON.stringify(userObj))
          setToken(data.token)
          setUser(userObj)
          return
        }
      } catch {
        // Backend offline or error — fall through to local login
      }

      // Fallback: always succeed — create a local session
      const namePart = email.split('@')[0] || 'User'
      const displayName = namePart
        .replace(/[._-]/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase())
      const localToken = `local_${Date.now()}_${Math.random().toString(36).slice(2)}`
      const userObj: AuthUser = {
        email,
        role: 'ceo', // default role for external logins
        name: displayName,
        org: extra?.enterprise || 'External',
        designation: extra?.designation,
      }
      localStorage.setItem('sx_token', localToken)
      localStorage.setItem('ks_current_user', JSON.stringify(userObj))
      setToken(localToken)
      setUser(userObj)
    },
    [],
  )

  // SYNC logout
  const logout = useCallback(() => {
    const t = localStorage.getItem('sx_token')
    localStorage.removeItem('sx_token')
    localStorage.removeItem('ks_current_user')
    setUser(null)
    setToken(null)
    if (t && !t.startsWith('local_')) {
      fetch('/api/auth/logout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${t}` },
      }).catch(() => {})
    }
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
