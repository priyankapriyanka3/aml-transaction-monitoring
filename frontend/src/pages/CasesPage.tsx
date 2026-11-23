import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

interface CaseListItem {
  case_id: string
  case_ref: string
  status: string
  current_blocker_state: string
  primary_alert_ref?: string
  created_at_utc: string
}

export function CasesPage() {
  const [cases, setCases] = useState<CaseListItem[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    // For now, we'll show a placeholder since the backend doesn't have a cases list endpoint yet
    // In a real implementation, this would call apiClient.getCases()
    setLoading(false)
    
    // Mock data for demonstration - in production this would come from the API
    setCases([
      {
        case_id: '1',
        case_ref: 'CS-201',
        status: 'INVESTIGATING',
        current_blocker_state: 'NONE',
        primary_alert_ref: 'ALT-20241120-001',
        created_at_utc: new Date().toISOString(),
      }
    ])
  }, [])

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'INVESTIGATING': return 'badge-info'
      case 'PENDING_INFORMATION': return 'badge-warning'
      case 'UNDER_REVIEW': return 'badge-primary'
      case 'APPROVED': return 'badge-success'
      case 'REJECTED': return 'badge-critical'
      default: return 'badge-neutral'
    }
  }

  const getBlockerBadgeClass = (blocker: string) => {
    if (blocker === 'NONE') return ''
    if (blocker === 'OVERDUE_REQUESTS') return 'badge-critical'
    return 'badge-warning'
  }

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div>
        <h1 className="headline-large">Cases</h1>
        <p className="body-medium text-muted">Investigation cases / most recent first</p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div className="spinner" style={{ borderColor: 'var(--primary)', margin: '0 auto' }} />
        </div>
      ) : cases.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p className="title-medium">No cases yet</p>
          <p className="body-medium text-muted">Cases created from alerts will appear here.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {cases.map((caseItem) => (
            <article
              key={caseItem.case_id}
              className="card"
              onClick={() => navigate(`/cases/${caseItem.case_id}/investigation`)}
              style={{ cursor: 'pointer' }}
              aria-label={`Case ${caseItem.case_ref}`}
            >
              <div className="flex justify-between items-center">
                <h3 className="title-small text-bold">{caseItem.case_ref}</h3>
                <span className={`badge ${getStatusBadgeClass(caseItem.status)}`}>
                  {caseItem.status.replace(/_/g, ' ')}
                </span>
              </div>
              
              {caseItem.primary_alert_ref && (
                <p className="body-medium">
                  Primary alert: <span className="text-bold">{caseItem.primary_alert_ref}</span>
                </p>
              )}
              
              <div className="flex justify-between items-center">
                <p className="body-small text-muted">
                  Created: {new Date(caseItem.created_at_utc).toLocaleString('en-GB', { timeZone: 'UTC' })} UTC
                </p>
                {caseItem.current_blocker_state !== 'NONE' && (
                  <span className={`badge ${getBlockerBadgeClass(caseItem.current_blocker_state)}`}>
                    {caseItem.current_blocker_state.replace(/_/g, ' ')}
                  </span>
                )}
              </div>
            </article>
          ))}
        </div>
      )}

      {/* Info banner */}
      <aside className="banner banner-info" role="note" aria-label="Cases information">
        <span className="icon">ℹ️</span>
        <div className="flex-col gap-xs">
          <p className="title-small">Cases are created from alerts</p>
          <p className="body-small" style={{ color: 'var(--on-info-container)' }}>
            To create a new case, navigate to an alert's evidence screen and use the "Create case" action.
          </p>
        </div>
      </aside>
    </div>
  )
}
