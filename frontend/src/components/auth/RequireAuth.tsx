// Route guard component that redirects to login if not authenticated
import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../lib/auth-context';

interface RequireAuthProps {
  children: ReactNode;
}

export function RequireAuth({ children }: RequireAuthProps) {
  const { isAuthenticated, isLoading } = useAuth();

  // Show nothing while checking authentication status
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="flex flex-col items-center gap-md">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-on-surface-variant text-bm">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Render protected content
  return <>{children}</>;
}
