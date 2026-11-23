import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export function LoginPage() {
  const [email, setEmail] = useState('investigator@example.com')
  const [password, setPassword] = useState('investigator123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate('/alerts')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--background)',
    }}>
      <div className="card" style={{
        width: '100%',
        maxWidth: '400px',
        margin: '16px',
      }}>
        <h1 className="headline-medium" style={{ marginBottom: '8px' }}>
          AML Workbench
        </h1>
        <p className="body-medium text-muted" style={{ marginBottom: '16px' }}>
          Sign in to continue
        </p>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label htmlFor="email" className="label-medium" style={{ display: 'block', marginBottom: '8px' }}>
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              required
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '1px solid var(--outline)',
                borderRadius: 'var(--radius-medium)',
                fontSize: '16px',
                fontFamily: 'var(--font-family)',
              }}
            />
          </div>

          <div>
            <label htmlFor="password" className="label-medium" style={{ display: 'block', marginBottom: '8px' }}>
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              required
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '1px solid var(--outline)',
                borderRadius: 'var(--radius-medium)',
                fontSize: '16px',
                fontFamily: 'var(--font-family)',
              }}
            />
          </div>

          {error && (
            <div className="banner banner-error">
              <span className="icon">⚠</span>
              <span className="body-small">{error}</span>
            </div>
          )}

          <button
            type="submit"
            className="btn btn-filled btn-block"
            disabled={loading}
          >
            {loading ? <span className="spinner" /> : 'Sign in'}
          </button>

          <p className="body-small text-muted" style={{ textAlign: 'center', marginTop: '8px' }}>
            Default: investigator@example.com / investigator123
          </p>
        </form>
      </div>
    </div>
  )
}
