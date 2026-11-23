import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

interface AppLayoutProps {
  children: ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const location = useLocation()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)

  const isAlertsPath = location.pathname.startsWith('/alerts')
  const isCasesPath = location.pathname.startsWith('/cases')

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--background)' }}>
      {/* App bar with navigation */}
      <header style={{
        background: 'var(--surface)',
        borderBottom: '0.5px solid var(--outline-variant)',
      }}>
        <div style={{ padding: '8px 16px 0' }}>
          <div className="flex justify-between items-center" style={{ marginBottom: '4px' }}>
            <p className="eyebrow">TRANSFER REVIEW · {user?.display_name || 'User'} · {user?.role || 'Investigator'}</p>
            <div className="flex items-center gap-xs">
              <span className="badge badge-primary">
                {user?.role || 'Investigator'}
              </span>
              <button
                onClick={() => logout()}
                className="btn btn-text"
                style={{ minHeight: '32px', height: '32px', fontSize: '12px' }}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
        
        {/* Primary navigation tabs */}
        <nav style={{ display: 'flex', borderTop: '0.5px solid var(--outline-variant)' }} role="navigation" aria-label="Main navigation">
          <Link
            to="/alerts"
            style={{
              flex: '1',
              minHeight: '48px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px',
              lineHeight: '20px',
              fontWeight: isAlertsPath ? '600' : '400',
              letterSpacing: '0.1px',
              color: isAlertsPath ? 'var(--primary)' : 'var(--on-surface-variant)',
              position: 'relative',
              textDecoration: 'none',
              textAlign: 'center',
              padding: '0 4px',
            }}
          >
            Alerts
            {isAlertsPath && (
              <span style={{
                position: 'absolute',
                left: '12px',
                right: '12px',
                bottom: '0',
                height: '3px',
                borderRadius: '3px 3px 0 0',
                background: 'var(--primary)',
              }} />
            )}
          </Link>
          <Link
            to="/cases"
            style={{
              flex: '1',
              minHeight: '48px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px',
              lineHeight: '20px',
              fontWeight: isCasesPath ? '600' : '400',
              letterSpacing: '0.1px',
              color: isCasesPath ? 'var(--primary)' : 'var(--on-surface-variant)',
              position: 'relative',
              textDecoration: 'none',
              textAlign: 'center',
              padding: '0 4px',
            }}
          >
            Cases
            {isCasesPath && (
              <span style={{
                position: 'absolute',
                left: '12px',
                right: '12px',
                bottom: '0',
                height: '3px',
                borderRadius: '3px 3px 0 0',
                background: 'var(--primary)',
              }} />
            )}
          </Link>
        </nav>
      </header>

      {/* Page content */}
      <main style={{ flex: 1 }}>
        {children}
      </main>
    </div>
  )
}
