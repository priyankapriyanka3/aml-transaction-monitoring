import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiClient } from '../api/client'
import type { AlertEvidenceResponse } from '../types/api'

export function AlertEvidencePage() {
  const { alertId } = useParams<{ alertId: string }>()
  const [evidence, setEvidence] = useState<AlertEvidenceResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [snackbar, setSnackbar] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    if (alertId) {
      loadEvidence(alertId)
    }
  }, [alertId])

  const loadEvidence = async (id: string) => {
    try {
      setLoading(true)
      const data = await apiClient.getAlertEvidence(id)
      setEvidence(data)
    } catch (error) {
      console.error('Failed to load evidence:', error)
      alert('Evidence could not be loaded')
      navigate('/alerts')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateCase = async () => {
    if (!alertId) return

    try {
      setCreating(true)
      const result = await apiClient.createCase(alertId)
      setSnackbar(`Case ${result.case_ref} created`)
      setTimeout(() => {
        navigate(`/cases/${result.case_id}/investigation`)
      }, 1500)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Case creation failed')
    } finally {
      setCreating(false)
    }
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

  const getOutcomeBadgeClass = (outcome: string) => {
    return outcome === 'MATCH' ? 'badge-critical' : 'badge-success'
  }

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--background)' }}>
        <div className="spinner" style={{ borderColor: 'var(--primary)', width: '40px', height: '40px' }} />
      </div>
    )
  }

  if (!evidence) {
    return null
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--background)' }}>
      {/* App bar */}
      <header style={{
        background: 'var(--surface)',
        borderBottom: '0.5px solid var(--outline-variant)',
        padding: '0 4px',
        minHeight: '64px',
        display: 'flex',
        alignItems: 'center',
      }}>
        <button
          className="btn btn-text"
          onClick={() => navigate('/alerts')}
          aria-label="Navigate up to alert queue"
          style={{ padding: '12px' }}
        >
          ← Back
        </button>
        <h1 className="title-large" style={{ flex: 1, paddingLeft: '4px' }}>
          {evidence.alert_ref}
        </h1>
        <button className="btn btn-text" aria-label={`View audit history for ${evidence.alert_ref}`}>
          🕐 Audit
        </button>
      </header>

      <main style={{ flex: 1, padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Header */}
        <div className="flex justify-between items-center flex-wrap gap-sm">
          <p className="eyebrow">TRANSFER REVIEW · ALERT EVIDENCE</p>
          <span className="badge badge-info">Status: {evidence.status}</span>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-sm" aria-label="Alert summary">
          <span className={`badge ${getPriorityBadgeClass(evidence.priority)}`}>
            {evidence.priority} · Score {evidence.risk_score}
          </span>
          <span className="badge badge-neutral">
            {evidence.transaction.source_country_code} → {evidence.transaction.destination_country_code}
          </span>
        </div>

        {/* Transaction facts card */}
        <section className="card card-elevated" aria-labelledby="facts-h">
          <h2 id="facts-h" className="title-medium">Transaction facts</h2>
          <p className="title-large text-bold">
            {evidence.transaction.currency_code} {parseFloat(evidence.transaction.amount).toLocaleString()}
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '112px 1fr', gap: '10px 12px', alignItems: 'start' }}>
            <dt className="label-medium text-muted">Customer</dt>
            <dd className="body-medium text-semibold" style={{ margin: 0 }}>
              {evidence.customer.customer_name}
              <span className="text-muted" style={{ fontWeight: 400 }}> · {evidence.customer.customer_id.slice(0, 8)}</span>
            </dd>
            
            <dt className="label-medium text-muted">Transaction</dt>
            <dd className="body-medium" style={{ margin: 0 }}>
              {evidence.transaction.transaction_ref} · International wire
            </dd>
            
            <dt className="label-medium text-muted">Date and time</dt>
            <dd className="body-medium" style={{ margin: 0 }}>
              {new Date(evidence.transaction.executed_at_utc).toLocaleString('en-GB', { 
                timeZone: 'UTC',
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })} UTC
            </dd>
            
            <dt className="label-medium text-muted">Account</dt>
            <dd className="body-medium" style={{ margin: 0 }}>
              {evidence.account.account_ref} · {evidence.account.account_type}
            </dd>
            
            <dt className="label-medium text-muted">Corridor</dt>
            <dd className="body-medium" style={{ margin: 0 }}>
              {evidence.transaction.source_country_code} → {evidence.transaction.destination_country_code}
            </dd>
            
            {evidence.customer.pep_flag && (
              <>
                <dt className="label-medium text-muted">Customer risk</dt>
                <dd className="body-medium" style={{ margin: 0 }}>
                  <span className="badge badge-warning">PEP</span>
                </dd>
              </>
            )}
          </div>
          <div style={{ height: '0.5px', background: 'var(--outline-variant)', margin: '4px 0' }} />
          <div className="flex items-center gap-sm flex-wrap" aria-label="Record relationship">
            <span style={{
              background: 'var(--surface-variant)',
              borderRadius: 'var(--radius-small)',
              padding: '4px 8px',
              fontSize: '12px',
              fontWeight: 500,
            }}>
              {evidence.alert_ref}
            </span>
            <span>→</span>
            <span style={{
              background: 'var(--surface-variant)',
              borderRadius: 'var(--radius-small)',
              padding: '4px 8px',
              fontSize: '12px',
              fontWeight: 500,
            }}>
              {evidence.transaction.transaction_ref}
            </span>
            <span>→</span>
            <span style={{
              background: 'var(--surface-variant)',
              borderRadius: 'var(--radius-small)',
              padding: '4px 8px',
              fontSize: '12px',
              fontWeight: 500,
            }}>
              {evidence.customer.customer_name}
            </span>
          </div>
        </section>

        {/* Rule evaluation snapshot card */}
        <section className="card" aria-labelledby="rules-h">
          <div className="flex justify-between items-center">
            <h2 id="rules-h" className="title-medium">Rule evaluation snapshot</h2>
            <span className="badge badge-neutral">
              🔒 Read-only
            </span>
          </div>
          
          <div className="banner banner-info" style={{ padding: '12px' }} role="note">
            <span className="icon">ℹ️</span>
            <p className="body-small" style={{ color: 'var(--on-info-container)' }}>
              Historical versions used at evaluation — not the latest rules.
            </p>
          </div>

          <div>
            {evidence.rule_snapshots.map((snapshot, _index) => (
              <div key={snapshot.snapshot_id} className="rule-row">
                <div className="rule-row-content">
                  <p className="body-medium text-semibold">
                    {snapshot.rule_name} · {snapshot.rule_version}
                  </p>
                  <p className="body-small text-muted">{snapshot.condition_text}</p>
                  <p className="body-small text-muted">
                    Evaluated {new Date(snapshot.evaluated_from_utc).toLocaleString('en-GB', {
                      timeZone: 'UTC',
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })} UTC
                  </p>
                </div>
                <span className={`badge ${getOutcomeBadgeClass(snapshot.outcome)}`}>
                  {snapshot.outcome === 'MATCH' ? '⚠️' : '✓'} {snapshot.outcome}
                </span>
              </div>
            ))}
          </div>
          
          <p className="body-small text-muted">
            {evidence.rule_snapshots.filter(s => s.outcome === 'MATCH').length} rules matched, 
            {' '}{evidence.rule_snapshots.filter(s => s.outcome === 'PASS').length} rules passed. 
            Snapshots are stored at evaluation time and cannot be edited.
          </p>
        </section>
      </main>

      {/* Sticky footer */}
      <footer style={{
        background: 'var(--surface-container-high)',
        borderTop: '0.5px solid var(--outline-variant)',
        flexShrink: 0,
      }}>
        <div style={{ padding: '12px 16px 4px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div className="flex gap-sm">
            <button
              className="btn btn-filled"
              style={{ flex: 1 }}
              onClick={handleCreateCase}
              disabled={creating}
              aria-label={`Create case from alert ${evidence.alert_ref}`}
            >
              {creating ? <span className="spinner" /> : (
                <>
                  <span style={{ fontSize: '18px' }}>+</span>
                  Create case
                </>
              )}
            </button>
            <button
              className="btn btn-outlined"
              style={{ flex: 1 }}
              aria-label={`Link alert ${evidence.alert_ref} to an existing case`}
            >
              🔗 Link to existing case
            </button>
          </div>
          <p className="body-small text-muted" style={{ textAlign: 'center' }}>
            Case creation carries the alert, transaction facts and rule snapshot forward.
          </p>
        </div>
      </footer>

      {/* Snackbar */}
      {snackbar && (
        <div className="snackbar">
          <span>{snackbar}</span>
          <button className="snackbar-action" onClick={() => setSnackbar('')}>
            View case
          </button>
        </div>
      )}
    </div>
  )
}
