import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import type { InformationRequestDetail } from '../types/api';
import '../styles/design-system.css';
import '../styles/components.css';

export default function RequestResolutionPage() {
  const { caseId, requestId } = useParams<{ caseId: string; requestId: string }>();
  const navigate = useNavigate();
  const [request, setRequest] = useState<InformationRequestDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [responseSummary, setResponseSummary] = useState('');
  const [receivedDate, setReceivedDate] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [showDiscardDialog, setShowDiscardDialog] = useState(false);
  const [snackbar, setSnackbar] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId || !requestId) return;
    loadRequest();
  }, [caseId, requestId]);

  const loadRequest = async () => {
    if (!caseId || !requestId) return;
    try {
      setLoading(true);
      const data = await apiClient.getInformationRequest(caseId, requestId);
      setRequest(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load information request');
    } finally {
      setLoading(false);
    }
  };

  const handleRecordResponse = async () => {
    setValidationErrors({});
    
    if (!responseSummary.trim()) {
      setValidationErrors((prev) => ({ ...prev, summary: 'Response summary is required.' }));
    }
    if (!receivedDate) {
      setValidationErrors((prev) => ({ ...prev, date: 'Received date is required.' }));
    }

    if (!responseSummary.trim() || !receivedDate || !caseId || !requestId) {
      return;
    }

    try {
      setSubmitting(true);
      await apiClient.recordResponse(caseId, requestId, {
        response_summary: responseSummary.trim(),
        received_at_utc: new Date(receivedDate).toISOString(),
      });
      setSnackbar(`Response recorded for ${request?.request_ref}`);
      setTimeout(() => {
        navigate(`/cases/${caseId}/investigation`);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to record response');
    } finally {
      setSubmitting(false);
    }
  };

  const handleBack = () => {
    if (responseSummary.trim() || receivedDate) {
      setShowDiscardDialog(true);
    } else {
      navigate(`/cases/${caseId}/investigation`);
    }
  };

  const handleDiscard = () => {
    setShowDiscardDialog(false);
    navigate(`/cases/${caseId}/investigation`);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return `${formatDate(dateString)}, ${date.toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    })} UTC`;
  };

  const getStatusBadgeClass = (status: string) => {
    const statusMap: Record<string, string> = {
      OPEN: 'b-warn',
      OVERDUE: 'b-crit',
      RESPONDED: 'b-ok',
      RESOLVED: 'b-ok',
    };
    return `badge ${statusMap[status] || 'b-neu'}`;
  };

  const getBlockerBannerClass = (blockerState: string) => {
    if (blockerState === 'OVERDUE_REQUESTS') return 'banner banner-crit';
    if (blockerState === 'OPEN_REQUESTS') return 'banner banner-warn';
    return 'banner banner-ok';
  };

  const getBlockerIcon = (blockerState: string) => {
    if (blockerState === 'OVERDUE_REQUESTS') return '⚠️';
    if (blockerState === 'OPEN_REQUESTS') return '⚠️';
    return '✓';
  };

  const getBlockerText = (blockerState: string) => {
    if (blockerState === 'OVERDUE_REQUESTS') return 'Overdue requests — decision blocked';
    if (blockerState === 'OPEN_REQUESTS') return 'Open requests — decision blocked';
    return 'No open requests — decision unblocked';
  };

  const getBlockerDescription = (blockerState: string) => {
    if (blockerState === 'OVERDUE_REQUESTS') {
      return 'This request is overdue. Approval, rejection and closure remain blocked while any request is open or overdue.';
    }
    if (blockerState === 'OPEN_REQUESTS') {
      return 'Approval, rejection and closure remain blocked while any request is open or overdue.';
    }
    return 'All requests have been resolved. Case can proceed to review.';
  };

  if (loading) {
    return (
      <div className="page">
        <div className="loading-state">Loading information request...</div>
      </div>
    );
  }

  if (error || !request) {
    return (
      <div className="page">
        <div className="error-state">
          <p>{error || 'Request not found'}</p>
          <button onClick={() => navigate(`/cases/${caseId}/investigation`)} className="btn btn-o">
            Back to case
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-header">
        <button onClick={handleBack} className="icon-btn" aria-label="Back to case investigation">
          ←
        </button>
        <div className="page-header-content">
          <p className="eyebrow">TRANSFER REVIEW · RESOLVE EVIDENCE GAPS</p>
          <h1 className="page-title">CS-{request.case_id.substring(0, 3)}</h1>
        </div>
      </header>

      <main className="page-content">
        <div className="row space-between">
          <span className={getStatusBadgeClass(request.status)}>
            {request.status}
          </span>
        </div>

        {request.blocker_state !== 'NONE' && (
          <div className={getBlockerBannerClass(request.blocker_state)} role="status" aria-live="polite">
            <span className="banner-icon">{getBlockerIcon(request.blocker_state)}</span>
            <div className="banner-content">
              <p className="banner-title">{getBlockerText(request.blocker_state)}</p>
              <p className="banner-text">{getBlockerDescription(request.blocker_state)}</p>
            </div>
          </div>
        )}

        <section className="card">
          <div className="row space-between">
            <h2 className="section-title">Request {request.request_ref}</h2>
            <span className={getStatusBadgeClass(request.status)}>{request.status}</span>
          </div>
          <dl className="detail-list">
            <dt>Due date</dt>
            <dd>{formatDate(request.due_at_utc)}</dd>
            <dt>Target</dt>
            <dd>{request.target_party}</dd>
            <dt>Channel</dt>
            <dd>{request.delivery_channel}</dd>
            <dt>Reason</dt>
            <dd>{request.reason_text}</dd>
            <dt>Raised</dt>
            <dd>{formatDateTime(request.created_at_utc)}</dd>
          </dl>
        </section>

        <section className="card">
          <h2 className="section-title">Record response</h2>

          <div className={`form-field form-field-multi ${validationErrors.summary ? 'form-field-error' : ''}`}>
            <label className="form-label">Response summary *</label>
            <textarea
              className="form-input"
              value={responseSummary}
              onChange={(e) => setResponseSummary(e.target.value)}
              placeholder="Describe what the documents prove..."
              rows={4}
            />
          </div>
          {validationErrors.summary && (
            <p className="form-helper form-helper-error">{validationErrors.summary}</p>
          )}
          <p className="form-helper">{responseSummary.length} / 1000</p>

          <div className={`form-field ${validationErrors.date ? 'form-field-error' : ''}`}>
            <label className="form-label">Received date *</label>
            <input
              type="date"
              className="form-input"
              value={receivedDate}
              onChange={(e) => setReceivedDate(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>
          {validationErrors.date && (
            <p className="form-helper form-helper-error">{validationErrors.date}</p>
          )}
          <p className="form-helper">Future dates are not allowed for evidence receipt.</p>
        </section>

        <footer className="page-footer">
          <button
            onClick={handleRecordResponse}
            disabled={submitting || !responseSummary.trim() || !receivedDate}
            className="btn btn-primary btn-block"
          >
            {submitting ? 'Recording...' : 'Record response'}
          </button>
          <p className="text-sm text-muted text-center">
            Recording clears the blocker and returns the case to Investigating.
          </p>
        </footer>
      </main>

      {showDiscardDialog && (
        <div className="dialog-overlay" onClick={() => setShowDiscardDialog(false)}>
          <div className="dialog" onClick={(e) => e.stopPropagation()} role="alertdialog">
            <h3 className="dialog-title">Discard unsaved response?</h3>
            <p className="dialog-text">
              You have entered a response summary{receivedDate && ' and selected a date'}. Going back now discards your changes.
            </p>
            <div className="dialog-actions">
              <button onClick={() => setShowDiscardDialog(false)} className="btn btn-text">
                Keep editing
              </button>
              <button onClick={handleDiscard} className="btn btn-text btn-danger">
                Discard
              </button>
            </div>
          </div>
        </div>
      )}

      {snackbar && (
        <div className="snackbar" role="status" aria-live="polite">
          {snackbar}
        </div>
      )}
    </div>
  );
}
