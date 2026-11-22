// Main application component with routing
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './lib/auth-context';
import { RequireAuth } from './components/auth/RequireAuth';
import { LoginPage } from './pages/LoginPage';
import { AlertQueuePage } from './pages/AlertQueuePage';
import { CaseWorkspacePage } from './pages/CaseWorkspacePage';
import { CaseEvidencePage } from './pages/CaseEvidencePage';
import { InformationRequestsPage } from './pages/InformationRequestsPage';
import { ReviewHandoffPage } from './pages/ReviewHandoffPage';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected routes */}
          <Route
            path="/alerts"
            element={
              <RequireAuth>
                <AlertQueuePage />
              </RequireAuth>
            }
          />

          {/* Cases route - redirects to alerts (main workqueue) */}
          <Route
            path="/cases"
            element={
              <RequireAuth>
                <Navigate to="/alerts" replace />
              </RequireAuth>
            }
          />

          <Route
            path="/cases/:caseId"
            element={
              <RequireAuth>
                <CaseWorkspacePage />
              </RequireAuth>
            }
          />

          <Route
            path="/cases/:caseId/evidence"
            element={
              <RequireAuth>
                <CaseEvidencePage />
              </RequireAuth>
            }
          />

          <Route
            path="/cases/:caseId/information-requests"
            element={
              <RequireAuth>
                <InformationRequestsPage />
              </RequireAuth>
            }
          />

          <Route
            path="/cases/:caseId/handoff"
            element={
              <RequireAuth>
                <ReviewHandoffPage />
              </RequireAuth>
            }
          />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/alerts" replace />} />

          {/* Catch-all redirect to alerts */}
          <Route path="*" element={<Navigate to="/alerts" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
