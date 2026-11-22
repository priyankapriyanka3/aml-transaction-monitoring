import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth-context';

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ username, password });
      
      // Navigate to alerts page
      navigate('/alerts');
    } catch (err) {
      if (err && typeof err === 'object' && 'detail' in err) {
        setError((err as { detail: string }).detail);
      } else {
        setError('Login failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="bg-surface rounded-xl p-8 shadow-md border border-outline-variant w-full max-w-md">
        <h1 className="text-3xl font-bold mb-2 text-on-surface">Login</h1>
        <p className="text-sm text-on-surface-variant mb-6">
          AML Transaction Monitoring & Compliance Workbench
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label htmlFor="username" className="text-xs font-medium text-on-surface-variant">
              Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="min-h-[56px] px-4 border border-outline rounded-xl bg-surface text-on-surface text-base focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Enter username"
              autoComplete="username"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="password" className="text-xs font-medium text-on-surface-variant">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="min-h-[56px] px-4 border border-outline rounded-xl bg-surface text-on-surface text-base focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Enter password"
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="bg-critical-container text-on-critical-container rounded-xl p-4 text-sm" role="alert">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="min-h-[48px] px-6 rounded-xl bg-primary text-on-primary text-sm font-semibold disabled:opacity-38"
          >
            {loading ? 'Logging in...' : 'Log in'}
          </button>

          <div className="text-xs text-on-surface-variant mt-2">
            <p className="font-semibold mb-1">Demo Credentials:</p>
            <p>Investigator: riya / password123</p>
            <p>Officer: morgan / password123</p>
          </div>
        </form>
      </div>
    </div>
  );
}
