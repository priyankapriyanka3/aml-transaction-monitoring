import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { LoginPage } from './pages/LoginPage'
import { AlertQueuePage } from './pages/AlertQueuePage'
import { AlertEvidencePage } from './pages/AlertEvidencePage'
import { CasesPage } from './pages/CasesPage'
import CaseInvestigationPage from './pages/CaseInvestigationPage'
import RequestResolutionPage from './pages/RequestResolutionPage'
import ReadinessPage from './pages/ReadinessPage'
import OfficerReviewPage from './pages/OfficerReviewPage'
import { AppLayout } from './components/AppLayout'
import { useAuthStore } from './stores/authStore'

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const initialize = useAuthStore((state) => state.initialize)

  useEffect(() => {
    initialize()
  }, [initialize])

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <AppLayout>
      <Routes>
        <Route path="/alerts" element={<AlertQueuePage />} />
        <Route path="/alerts/:alertId/evidence" element={<AlertEvidencePage />} />
        <Route path="/cases" element={<CasesPage />} />
        <Route path="/cases/:caseId/investigation" element={<CaseInvestigationPage />} />
        <Route path="/cases/:caseId/requests/:requestId" element={<RequestResolutionPage />} />
        <Route path="/cases/:caseId/readiness" element={<ReadinessPage />} />
        <Route path="/cases/:caseId/officer-review" element={<OfficerReviewPage />} />
        <Route path="/" element={<Navigate to="/alerts" replace />} />
      </Routes>
    </AppLayout>
  )
}

export default App
