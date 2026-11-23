import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import type { ReadinessProjection } from '../types/api';
import '../styles/design-system.css';
import '../styles/components.css';

export default function ReadinessPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [readiness, setReadiness] = useState<ReadinessProjection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOfficerId, setSelectedOfficerId] = useState<string | null>(null);
  const [sharing, setSharing] = useState(false);
  const [snackbar, setSnackbar] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) return;
    loadReadiness();
  }, [caseId]);

  const loadReadiness = async () => {
    if (!caseId) return;
    try {
      setLoading(true);
      const data = await apiClient.getCaseReadiness(caseId);
      setReadiness(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load readiness');
    } finally {
      setLoading(false);
    }
  };

  const handleOfficerChange = async (officerId: string) => {
    if (!caseId) return;
    try {
      setSelectedOfficerId(officerId);
      await apiClient.assignOfficer(caseId, officerId);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to assign officer');
      setSelectedOfficerId(null);
    }
  };

  const handleShareForReview = async () => {
    if (!caseId || !readiness) return;

    const allComplete = readiness.checklist.every((item) => item.complete);
    if (!allComplete) {
      setError('All checklist items must be complete before sharing');
      return;
    }

    if (!selectedOfficerId) {
      setError('Please select an officer before sharing');
      return;
    }

    try {
      setSharing(true);
      await apiClient.shareForReview(caseId);
      setSnackbar('Case shared for officer review');
      setTimeout(() => {
        navigate(`/cases/${caseId}/investigation`);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to share for review');
    } finally {
      setSharing(false);
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="loading-state">Loading readiness checklist...</div>
      </div>
    );
  }

  if (error && !readiness) {
    return (
      <div className="page">
        <div className="error-state">
          <p>{error}</p>
          <button onClick={() => navigate(`/cases/${caseId}/investigation`)} className="btn btn-o">
            Back to case
          </button>
        </div>
      </div>
    );
  }

  if (!readiness) {
    return (
      <div className="page">
        <div className="error-state">
          <p>Readiness data not found</p>
        </div>
      </div>
    );
  }

  const allComplete = readiness.checklist.every((item) => item.complete);
  const canShare = allComplete && selectedOfficerId !== null;

  return (
    <div className="page">
      <header className="page-header">
        <button
          onClick={() => navigate(`/cases/${caseId}/investigation`)}
          className="icon-btn"
          aria-label="Back to case investigation"
        >
          ←
        </button>
        <div className="page-header-content">
          <p className="eyebrow">TRANSFER REVIEW · 05 OF 06</p>
          <h1 className="page-title">Review readiness</h1>
        </div>
      </header>

      <main className="page-content">
        <div className="row space-between">
          <span className={`badge ${allComplete ? 'b-ok' : 'b-warn'}`}>
            {allComplete ? '✓ Ready for review' : 'Incomplete'}
          </span>
          <p className="text-sm text-muted">Case status: Investigating</p>
        </div>

        {error && (
          <div className="banner banner-warn" role="alert">
            <span className="banner-icon">⚠️</span>
            <div className="banner-content">
              <p className="banner-text">{error}</p>
            </div>
          </div>
        )}

        {/* Readiness Checklist */}
        <section className="card">
          <div className="row space-between">
            <h2 className="section-title">Readiness checklist</h2>
            <span className={`badge ${allComplete ? 'b-ok' : 'b-neu'}`}>
              {readiness.checklist.filter((i) => i.complete).length} of {readiness.checklist.length} complete
            </span>
          </div>

          <div className="checklist">
            {readiness.checklist.map((item) => (
              <div key={item.name} className="checklist-item">
                <span className={`checklist-icon ${item.complete ? 'complete' : 'incomplete'}`}>
                  {item.complete ? '✓' : '○'}
                </span>
                <div className="checklist-content">
                  <p className="checklist-title">
                    {item.name === 'linked_evidence' && 'Linked evidence'}
                    {item.name === 'investigation_notes' && 'Investigation notes'}
                    {item.name === 'responses_reviewed' && 'Responses reviewed'}
                    {item.name === 'no_open_requests' && 'No open or overdue requests'}
                    <span className={`badge ${item.complete ? 'b-ok' : 'b-warn'}`} style={{ marginLeft: '8px' }}>
                      {item.complete ? 'Complete' : 'Incomplete'}
                    </span>
                  </p>
                  <p className="text-sm text-muted">{item.details}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Review Package Summary */}
        <section className="card">
          <h2 className="section-title">Review package</h2>
          <p className="text-sm text-muted">
            What the officer will receive. Everything below is read-only once shared.
          </p>

          <div className="list-group">
            <div className="list-item">
              <div className="list-item-content">
                <p className="list-item-title">Alerts · {readiness.package_summary.alert_count}</p>
                <p className="text-sm text-muted">
                  {readiness.package_summary.alert_count === 1
                    ? '1 alert linked'
                    : `${readiness.package_summary.alert_count} alerts linked`}
                </p>
              </div>
              <span className="list-item-action">→</span>
            </div>

            <div className="list-item">
              <div className="list-item-content">
                <p className="list-item-title">Investigation notes · {readiness.package_summary.note_count}</p>
                <p className="text-sm text-muted">
                  {readiness.package_summary.note_count === 1
                    ? '1 note recorded'
                    : `${readiness.package_summary.note_count} notes recorded`}
                </p>
              </div>
              <span className="list-item-action">→</span>
            </div>

            <div className="list-item">
              <div className="list-item-content">
                <p className="list-item-title">Information requests · {readiness.package_summary.request_count}</p>
                <p className="text-sm text-muted">
                  {readiness.package_summary.request_count === 0
                    ? 'No requests'
                    : `${readiness.package_summary.request_count} request(s)`}
                </p>
              </div>
              <span className="list-item-action">→</span>
            </div>

            <div className="list-item">
              <div className="list-item-content">
                <p className="list-item-title">Historical rule context</p>
                <p className="text-sm text-muted">Rule evaluation snapshots at alert generation</p>
              </div>
              <span className="list-item-action">→</span>
            </div>
          </div>
        </section>

        {/* Four-Eyes Officer Assignment */}
        <section className="card card-four-eyes">
          <div className="row">
            <span className="card-icon" style={{ color: '#005FCC' }}>
              🛡️
            </span>
            <h2 className="section-title">Independent review required</h2>
          </div>

          <p className="text-base">
            Case creator cannot decide this case. The reviewing officer must be a different person.
          </p>

          <div className={`field ${!selectedOfficerId ? 'field-error' : ''}`}>
            <label className="field-label">Reviewing officer *</label>
            <select
              className="field-select"
              value={selectedOfficerId || ''}
              onChange={(e) => handleOfficerChange(e.target.value)}
              aria-label="Select reviewing officer"
            >
              <option value="">Select an officer</option>
              {readiness.eligible_officers.map((officer) => (
                <option key={officer.user_id} value={officer.user_id}>
                  {officer.display_name} ({officer.email})
                </option>
              ))}
            </select>
          </div>

          {!selectedOfficerId && (
            <p className="helper-text helper-error">Choose an independent officer before sharing.</p>
          )}

          <p className="text-sm text-muted">
            Case creator is not selectable. Assignment is recorded with case ID, officer, assigning user and UTC time.
          </p>
        </section>
      </main>

      <footer className="page-footer">
        <button
          onClick={handleShareForReview}
          disabled={!canShare || sharing}
          className={`btn btn-f block ${!canShare || sharing ? 'btn-disabled' : ''}`}
          aria-label="Share case for officer review"
        >
          {sharing ? 'Sharing...' : 'Share for officer review'}
        </button>
        <p className="text-sm text-muted text-center">
          Sharing moves the case to Under review and notifies the officer.
        </p>
      </footer>

      {snackbar && (
        <div className="snackbar" role="status">
          {snackbar}
        </div>
      )}
    </div>
  );
}
