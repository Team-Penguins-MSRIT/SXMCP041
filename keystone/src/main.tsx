import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import App from './App'
import './index.css'

function Shell() {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0a0a0f] font-mono text-sm text-indigo-400">
        Initializing…
      </div>
    )
  }
  if (!user) return <LoginPage />
  return <App />
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <Shell />
    </AuthProvider>
  </StrictMode>,
)
