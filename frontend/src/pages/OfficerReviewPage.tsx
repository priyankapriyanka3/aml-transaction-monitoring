import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import type { OfficerReviewPackage } from '../types/api';
import '../styles/design-system.css';
import '../styles/components.css';

type DecisionOutcome = 'APPROVE' | 'REJECT' | 'ESCALATE' | 'FALSE_POSITIVE';

export default function OfficerReviewPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [reviewPackage, setReviewPackage] = useState<OfficerReviewPackage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOutcome, setSelectedOutcome] = useState<DecisionOutcome | null>(null);
  const [rationaleText, setRationaleText] = useState('');
  const [recording, setRecording] = useState(false);
  const [snackbar, setSnackbar] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) return;
    loadReviewPackage();
  }, [caseId]);

  const loadReviewPackage = async () => {
    if (!caseId) return;
    try {
      setLoading(true);
      const data = await apiClient.getOfficerReviewPackage(caseId);
      setReviewPackage(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load review package');
    } finally {
      setLoading(false);
    }
  };

  const handleRecordDecision = async () => {
    if (!caseId || !selectedOutcome || !rationaleText.trim()) return;

    try {
      setRecording(true);
      await apiClient.recordDecision(caseId, {
        outcome: selectedOutcome,
        rationale_text: rationaleText.trim(),
      });
      setSnackbar(`Decision recorded for ${reviewPackage?.case_ref || 'case'}`);
      setTimeout(() => {
        navigate('/cases');
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to record decision');
    } finally {
      setRecording(false);
    }
  };

  const getOutcomeLabel = (outcome: DecisionOutcome): string => {
    const labels: Record<DecisionOutcome, string> = {
      APPROVE: 'Approve',
      REJECT: 'Reject',
      ESCALATE: 'Escalate',
      FALSE_POSITIVE: 'Close as false positive',
    };
    return labels[outcome];
  };

  const getOutcomePreviewLabel = (outcome: DecisionOutcome): string => {
    const labels: Record<DecisionOutcome, string> = {
      APPROVE: 'Approved',
      REJECT: 'Rejected',
      ESCALATE: 'Escalated',
      FALSE_POSITIVE: 'Closed · False positive',
    };
    return labels[outcome];
  };

  if (loading) {
    return (
      <div className="page">
        <div className="loading-state">Loading officer review package...</div>
      </div>
    );
  }

  if (error && !reviewPackage) {
    return (
      <div className="page">
        <div className="error-state">
          <p>{error}</p>
          <button onClick={() => navigate('/cases')} className="btn btn-o">
            Back to cases
          </button>
        </div>
      </div>
    );
  }

  if (!reviewPackage) {
    return (
      <div className="page">
        <div className="error-state">
          <p>Review package not found</p>
        </div>
      </div>
    );
  }

  const hasBlocker = reviewPackage.blocker_state !== 'NONE';
  const isConflicted = reviewPackage.is_conflicted_officer;
  const canRecordDecision =
    !hasBlocker && !isConflicted && selectedOutcome !== null && rationaleText.trim().length > 0;

  return (
    <div className="page">
      <header className="page-header">
        <button onClick={() => navigate('/cases')} className="icon-btn" aria-label="Back to review queue">
          ←
        </button>
        <div className="page-header-content">
          <p className="eyebrow">TRANSFER REVIEW · 06 OF 06</p>
          <h1 className="page-title">{reviewPackage.case_ref} · Officer review</h1>
        </div>
      </header>

      <main className="page-content">
        <div className="row space-between">
          <span className="badge b-warn">⚠️ PENDING DECISION</span>
          <p className="text-sm text-muted">Reviewing as AML Officer</p>
        </div>

        {/* Blocker Banner */}
        {hasBlocker && (
          <div className="banner banner-warn" role="status" aria-live="polite">
            <span className="banner-icon">⚠️</span>
            <div className="banner-content">
              <p className="banner-title">
                {reviewPackage.blocker_state === 'OPEN_REQUESTS' ? 'Open requests — decision blocked' : 'Overdue requests — decision blocked'}
              </p>
              <p className="banner-text">
                Approval, rejection and closure remain blocked while any request is open or overdue.
              </p>
            </div>
          </div>
        )}

        {/* Conflicted Officer Banner */}
        {isConflicted && (
          <div className="banner banner-crit" role="alert">
            <span className="banner-icon">🛡️</span>
            <div className="banner-content">
              <p className="banner-title">Independent review required</p>
              <p className="banner-text">Case creator cannot perform this action.</p>
            </div>
          </div>
        )}

        {/* Success Banner (no blockers) */}
        {!hasBlocker && !isConflicted && (
          <div className="banner banner-ok" role="status" aria-live="polite">
            <span className="banner-icon">✓</span>
            <div className="banner-content">
              <p className="banner-title">No open or overdue requests — decision available</p>
              <p className="banner-text">All information requests resolved. Nothing blocks a decision on {reviewPackage.case_ref}.</p>
            </div>
          </div>
        )}

        {error && (
          <div className="banner banner-warn" role="alert">
            <span className="banner-icon">⚠️</span>
            <div className="banner-content">
              <p className="banner-text">{error}</p>
            </div>
          </div>
        )}

        {/* Executive Summary */}
        <section className="card">
          <h2 className="section-title">Executive summary</h2>

          <div className="summary-content">
            <p className="text-base">
              Review package for {reviewPackage.case_ref} with {reviewPackage.linked_alerts.length} linked alert(s),{' '}
              {reviewPackage.notes.length} investigation note(s), and {reviewPackage.rule_snapshots.length} rule evaluation
              snapshot(s).
            </p>
          </div>

          <div className="hr"></div>

          <dl className="key-value-list">
            <dt>Linked alerts</dt>
            <dd>
              {reviewPackage.linked_alerts.map((alert, index) => (
                <span key={alert.alert_id}>
                  {alert.alert_ref}
                  {alert.is_primary && ' (primary)'}
                  {index < reviewPackage.linked_alerts.length - 1 && ' · '}
                </span>
              ))}
            </dd>

            <dt>Investigation notes</dt>
            <dd>{reviewPackage.notes.length} note(s) recorded</dd>

            <dt>Status</dt>
            <dd>{reviewPackage.status.replace(/_/g, ' ').toLowerCase()}</dd>
          </dl>

          <div className="hr"></div>

          <p className="text-sm text-muted font-semibold">Rule snapshots at evaluation</p>

          <div className="rule-list">
            {reviewPackage.rule_snapshots.map((rule) => (
              <div key={rule.snapshot_id} className="rule-item">
                <div className="rule-content">
                  <p className="rule-title">
                    {rule.rule_name} · {rule.rule_version}
                  </p>
                </div>
                <span className={`badge ${rule.outcome === 'MATCH' ? 'b-crit' : 'b-ok'}`}>
                  {rule.outcome === 'MATCH' ? '⚠️ MATCH' : '✓ PASS'}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Decision Recording */}
        <section className="card">
          <h2 className="section-title">Record decision</h2>

          <div className="decision-options" role="radiogroup" aria-label="Decision outcome">
            {(['APPROVE', 'REJECT', 'ESCALATE', 'FALSE_POSITIVE'] as DecisionOutcome[]).map((outcome) => (
              <button
                key={outcome}
                className={`decision-option ${selectedOutcome === outcome ? 'selected' : ''} ${hasBlocker || isConflicted ? 'disabled' : ''}`}
                onClick={() => !hasBlocker && !isConflicted && setSelectedOutcome(outcome)}
                disabled={hasBlocker || isConflicted}
                role="radio"
                aria-checked={selectedOutcome === outcome}
              >
                <span className="decision-radio">{selectedOutcome === outcome ? '◉' : '○'}</span>
                <span className="decision-label">{getOutcomeLabel(outcome)}</span>
              </button>
            ))}
          </div>

          <div className={`field field-multiline ${rationaleText.trim().length > 0 ? 'field-focus' : ''}`}>
            <label className="field-label">Reason *</label>
            <textarea
              className="field-textarea"
              value={rationaleText}
              onChange={(e) => setRationaleText(e.target.value)}
              placeholder="Explain why this outcome is justified"
              rows={4}
              disabled={hasBlocker || isConflicted}
              aria-label="Decision rationale"
            />
          </div>

          {selectedOutcome && rationaleText.trim().length > 0 && (
            <p className="helper-text">Outcome on record: {getOutcomePreviewLabel(selectedOutcome)}</p>
          )}

          {!selectedOutcome && (
            <p className="helper-text helper-error">Select an outcome before recording the decision.</p>
          )}

          {selectedOutcome && rationaleText.trim().length === 0 && (
            <p className="helper-text helper-error">Rationale is required before recording the final decision.</p>
          )}

          <button className="btn btn-t block" onClick={() => navigate(`/cases/${caseId}/investigation`)}>
            Return for further investigation
          </button>
        </section>

        {/* Compliance Notice */}
        <aside className="banner banner-info" role="note" aria-label="Audit compliance notice">
          <span className="banner-icon">🔒</span>
          <div className="banner-content">
            <p className="banner-title">Permanent record</p>
            <p className="banner-text">
              Your decision and rationale are recorded permanently with your user ID, role and UTC time. They cannot be
              edited or deleted afterwards.
            </p>
          </div>
        </aside>
      </main>

      <footer className="page-footer">
        <button
          onClick={handleRecordDecision}
          disabled={!canRecordDecision || recording}
          className={`btn btn-f block ${!canRecordDecision || recording ? 'btn-disabled' : ''}`}
          aria-label="Record decision"
        >
          {recording ? 'Recording...' : 'Record decision'}
        </button>
        <p className="text-sm text-muted text-center">
          {selectedOutcome
            ? `Records ${getOutcomePreviewLabel(selectedOutcome)} for ${reviewPackage.case_ref}.`
            : 'Select outcome and provide rationale to record decision.'}
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
