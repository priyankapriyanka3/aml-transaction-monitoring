import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../api/client'
import type { AlertQueueItem } from '../types/api'

export function AlertQueuePage() {
  const [alerts, setAlerts] = useState<AlertQueueItem[]>([])
  const [loading, setLoading] = useState(true)
  const [assigningId, setAssigningId] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [priorityFilter, setPriorityFilter] = useState<string>('')
  const [ownershipFilter, setOwnershipFilter] = useState<string>('Unassigned')
  const [statusFilter, setStatusFilter] = useState<string>('New')
  const [snackbar, setSnackbar] = useState<string>('')
  const [total, setTotal] = useState(0)
  const navigate = useNavigate()

  const loadAlerts = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getAlertQueue({
        search: search || undefined,
        priority: priorityFilter || undefined,
        ownership: ownershipFilter || undefined,
        status: statusFilter || undefined,
      })
      setAlerts(response.items)
      setTotal(response.total)
    } catch (error) {
      console.error('Failed to load alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAlerts()
  }, [search, priorityFilter, ownershipFilter, statusFilter])

  const handleAssign = async (alertId: string, alertRef: string) => {
    try {
      setAssigningId(alertId)
      await apiClient.assignAlert(alertId)
      setSnackbar(`Alert ${alertRef} assigned to you`)
      setTimeout(() => setSnackbar(''), 3000)
      await loadAlerts()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Assignment failed')
    } finally {
      setAssigningId(null)
    }
  }

  const handleCardClick = (alert: AlertQueueItem) => {
    navigate(`/alerts/${alert.alert_id}/evidence`)
  }

  const getPriorityBadgeClass = (priority: string) => {
    switch (priority) {
      case 'Critical': return 'badge-critical'
      case 'High': return 'badge-warning'
      case 'Medium': return 'badge-info'
      case 'Low': return 'badge-neutral'
      default: return 'badge-neutral'
    }
  }

  const heroAlert = alerts[0]
  const otherAlerts = alerts.slice(1)

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Page header */}
      <div>
        <h1 className="headline-large">Alerts</h1>
        <p className="body-medium text-muted">Review queue / highest priority first</p>
      </div>

      {/* Search */}
      <div className="search-field">
        <span className="icon">🔍</span>
        <input
          type="search"
          placeholder="Search alert, customer or transaction ID"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search alerts"
        />
      </div>

      {/* Filters */}
      <div className="chips" role="group" aria-label="Queue filters">
        <button
          className={`chip ${priorityFilter === '' ? 'chip-selected' : ''}`}
          onClick={() => setPriorityFilter('')}
        >
          {priorityFilter === '' && <span className="icon">✓</span>}
          Priority: All
        </button>
        <button
          className={`chip ${ownershipFilter === 'Unassigned' ? 'chip-selected' : ''}`}
          onClick={() => setOwnershipFilter(ownershipFilter === 'Unassigned' ? '' : 'Unassigned')}
        >
          {ownershipFilter === 'Unassigned' && <span className="icon">✓</span>}
          Owner: Unassigned
        </button>
        <button
          className={`chip ${statusFilter === 'New' ? 'chip-selected' : ''}`}
          onClick={() => setStatusFilter(statusFilter === 'New' ? '' : 'New')}
        >
          {statusFilter === 'New' && <span className="icon">✓</span>}
          Status: New
        </button>
      </div>

      {/* Queue header */}
      <div className="flex justify-between items-center">
        <h2 className="title-small">{total} alerts · highest priority first</h2>
        <span className="body-small text-muted">Refreshed {new Date().toLocaleString('en-GB', { timeZone: 'UTC' })} UTC</span>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div className="spinner" style={{ borderColor: 'var(--primary)', margin: '0 auto' }} />
        </div>
      ) : alerts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p className="title-medium">No alerts match these filters</p>
          <p className="body-medium text-muted">Clear a filter to see more alerts.</p>
        </div>
      ) : (
        <>
          {/* Hero alert card */}
          {heroAlert && (
            <article
              className="card card-hero"
              onClick={() => handleCardClick(heroAlert)}
              style={{ cursor: 'pointer' }}
              aria-label={`Alert ${heroAlert.alert_ref}`}
            >
              <div className="flex justify-between items-center">
                <h3 className="title-small text-bold">{heroAlert.alert_ref}</h3>
                <span className={`badge ${getPriorityBadgeClass(heroAlert.priority)}`}>
                  {heroAlert.priority} · Score {heroAlert.risk_score}
                </span>
              </div>
              <p className="body-medium text-muted">International wire</p>
              <div className="flex justify-between items-center">
                <p className="title-large text-bold">
                  {heroAlert.transaction_currency_code} {parseFloat(heroAlert.transaction_amount).toLocaleString()}
                </p>
                <span className="badge badge-neutral">
                  {heroAlert.source_country_code} → {heroAlert.destination_country_code}
                </span>
              </div>
              <div className="flex-col gap-xs">
                <p className="body-medium">Customer: {heroAlert.customer_name}</p>
                <p className="body-small text-muted">
                  Status: {heroAlert.status} · Owner: {heroAlert.owner_user_id ? 'Assigned' : 'Unassigned'}
                </p>
              </div>
              {!heroAlert.owner_user_id && (
                <>
                  <button
                    className="btn btn-filled btn-block"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleAssign(heroAlert.alert_id, heroAlert.alert_ref)
                    }}
                    disabled={assigningId === heroAlert.alert_id}
                    aria-label={`Assign alert ${heroAlert.alert_ref} to me`}
                  >
                    {assigningId === heroAlert.alert_id ? <span className="spinner" /> : 'Assign to me'}
                  </button>
                  <p className="body-small text-muted">Assignment moves this alert to Under review.</p>
                </>
              )}
            </article>
          )}

          {/* Other alerts */}
          {otherAlerts.length > 0 && (
            <>
              <h2 className="title-small">More in queue</h2>
              {otherAlerts.map((alert) => (
                <article
                  key={alert.alert_id}
                  className="card"
                  onClick={() => handleCardClick(alert)}
                  style={{ cursor: 'pointer' }}
                  aria-label={`Alert ${alert.alert_ref}`}
                >
                  <div className="flex justify-between items-center">
                    <h3 className="title-small text-bold">{alert.alert_ref}</h3>
                    <span className={`badge ${getPriorityBadgeClass(alert.priority)}`}>
                      {alert.priority} · Score {alert.risk_score}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <p className="title-medium">
                      {alert.transaction_currency_code} {parseFloat(alert.transaction_amount).toLocaleString()}
                    </p>
                    <span className="badge badge-neutral">
                      {alert.source_country_code} → {alert.destination_country_code}
                    </span>
                  </div>
                  <p className="body-medium">Customer: {alert.customer_name}</p>
                  <div className="flex justify-between items-center">
                    <p className="body-small text-muted">
                      Status: {alert.status} · Owner: {alert.owner_user_id ? 'Assigned' : 'Unassigned'}
                    </p>
                    {!alert.owner_user_id ? (
                      <button
                        className="btn btn-text"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleAssign(alert.alert_id, alert.alert_ref)
                        }}
                        disabled={assigningId === alert.alert_id}
                        aria-label={`Assign alert ${alert.alert_ref} to me`}
                      >
                        {assigningId === alert.alert_id ? <span className="spinner" style={{ borderColor: 'var(--primary)' }} /> : 'Assign to me'}
                      </button>
                    ) : (
                      <span className="badge badge-info">Owned</span>
                    )}
                  </div>
                </article>
              ))}
            </>
          )}

          {/* Audit banner */}
          <aside className="banner banner-info" role="note" aria-label="Audit guidance">
            <span className="icon">ℹ️</span>
            <div className="flex-col gap-xs">
              <p className="title-small">Every action here is audited</p>
              <p className="body-small" style={{ color: 'var(--on-info-container)' }}>
                Assigning, opening and filtering are written to the audit trail with your user ID, role and UTC time.
              </p>
            </div>
          </aside>
        </>
      )}

      {/* Snackbar */}
      {snackbar && (
        <div className="snackbar">
          <span>{snackbar}</span>
          <button className="snackbar-action" onClick={() => setSnackbar('')}>
            Dismiss
          </button>
        </div>
      )}
    </div>
  )
}
