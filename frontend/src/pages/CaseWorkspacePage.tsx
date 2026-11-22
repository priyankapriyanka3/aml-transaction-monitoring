import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../lib/api-client';
import { CaseOverview, CaseNote, CaseNoteRequest, RecommendationRequest } from '../types/case';
import { CaseHeader } from '../components/cases/CaseHeader';
import { InvestigationNotesPanel } from '../components/cases/InvestigationNotesPanel';
import { RecommendationPanel } from '../components/cases/RecommendationPanel';
import { formatCurrency, formatDateTime, cn } from '../lib/utils';

export function CaseWorkspacePage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();

  const [caseData, setCaseData] = useState<CaseOverview | null>(null);
  const [notes, setNotes] = useState<CaseNote[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'alerts' | 'requests' | 'activity'>('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (caseId) {
      loadCaseData();
      loadNotes();
    }
  }, [caseId]);

  const loadCaseData = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await apiClient.get<CaseOverview>(`/cases/${caseId}`);
      setCaseData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load case');
    } finally {
      setLoading(false);
    }
  };

  const loadNotes = async () => {
    try {
      const response = await apiClient.get<CaseNote[]>(`/cases/${caseId}/notes`);
      setNotes(response);
    } catch (err) {
      console.error('Failed to load notes:', err);
    }
  };

  const handleSaveNote = async (request: CaseNoteRequest) => {
    await apiClient.post<CaseNote>(`/cases/${caseId}/notes`, request);
    // Reload notes
    await loadNotes();
  };

  const handleSubmitRecommendation = async (request: RecommendationRequest) => {
    await apiClient.post(`/cases/${caseId}/recommendation`, request);
    // Reload case data to reflect new recommendation state
    await loadCaseData();
    // Navigate to handoff page (placeholder for now)
    navigate(`/cases/${caseId}/handoff`);
  };

  const priorityBadgeClass = cn(
    'inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium',
    {
      'bg-critical-container text-on-critical-container': caseData?.priority === 'CRITICAL',
      'bg-warning-container text-on-warning-container': caseData?.priority === 'HIGH',
      'bg-info-container text-on-info-container': caseData?.priority === 'MEDIUM',
    }
  );

  const hasOpenRequests = (caseData?.open_information_request_count || 0) > 0;
  const hasOverdueRequests = (caseData?.overdue_information_request_count || 0) > 0;
  const isRecommendationBlocked = hasOpenRequests || hasOverdueRequests;

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="bg-critical-container text-on-critical-container rounded-2xl p-4 max-w-md">
          <p className="text-sm font-medium">{error || 'Case not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-32">
      {/* Case Header */}
      <CaseHeader
        caseNumber={caseData.case_number}
        customerName={caseData.assigned_user_name || 'N/A'}
        status={caseData.status}
      />

      {/* Secondary Tabs */}
      <nav
        className="bg-surface border-b border-outline-variant flex overflow-x-auto"
        role="tablist"
        aria-label="Case sections"
      >
        <button
          role="tab"
          aria-selected={activeTab === 'overview'}
          onClick={() => setActiveTab('overview')}
          className={`flex-none min-h-[48px] px-3 text-sm border-b-[3px] ${
            activeTab === 'overview'
              ? 'text-primary font-semibold border-primary'
              : 'text-on-surface-variant border-transparent'
          }`}
        >
          Overview
        </button>
        <Link
          to={`/cases/${caseId}/evidence`}
          role="tab"
          aria-selected={activeTab === 'alerts'}
          className={`flex-none min-h-[48px] px-3 text-sm border-b-[3px] ${
            activeTab === 'alerts'
              ? 'text-primary font-semibold border-primary'
              : 'text-on-surface-variant border-transparent'
          }`}
        >
          Linked alerts ({caseData.linked_alert_count})
        </Link>
        <Link
          to={`/cases/${caseId}/information-requests`}
          role="tab"
          aria-selected={activeTab === 'requests'}
          className={`flex-none min-h-[48px] px-3 text-sm border-b-[3px] ${
            activeTab === 'requests'
              ? 'text-primary font-semibold border-primary'
              : 'text-on-surface-variant border-transparent'
          }`}
        >
          Requests ({caseData.open_information_request_count + caseData.overdue_information_request_count})
        </Link>
        <button
          role="tab"
          aria-selected={activeTab === 'activity'}
          onClick={() => setActiveTab('activity')}
          className={`flex-none min-h-[48px] px-3 text-sm border-b-[3px] ${
            activeTab === 'activity'
              ? 'text-primary font-semibold border-primary'
              : 'text-on-surface-variant border-transparent'
          }`}
        >
          Activity
        </button>
      </nav>

      {/* Main Content */}
      <main className="px-4 py-6 flex flex-col gap-6">
        {/* Decision Blocker Banner */}
        {(hasOpenRequests || hasOverdueRequests) && (
          <div
            className="bg-warning-container text-on-warning-container rounded-2xl p-4 flex gap-3"
            role="status"
            aria-live="polite"
          >
            <svg className="w-6 h-6 flex-none" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
            </svg>
            <div>
              <p className="text-sm font-medium">
                {caseData.open_information_request_count} open request — decision blocked
              </p>
              <p className="text-xs">
                Approval, rejection and closure remain blocked while any request is open or overdue.
              </p>
            </div>
          </div>
        )}

        {/* Case Summary Card */}
        <section
          className="bg-surface-container-low border border-surface-container-low rounded-xl p-4 flex flex-col gap-3"
          aria-labelledby="h-sum"
        >
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-lg font-semibold text-on-surface" id="h-sum">
              Case summary
            </h2>
            <span className={priorityBadgeClass}>
              {caseData.priority}
            </span>
          </div>

          <dl className="grid grid-cols-2 gap-x-4 gap-y-3">
            <div>
              <dt className="text-xs font-medium text-on-surface-variant">Case ID</dt>
              <dd className="text-sm font-semibold text-on-surface">{caseData.case_number}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-on-surface-variant">Owner</dt>
              <dd className="text-sm text-on-surface">{caseData.assigned_user_name}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-on-surface-variant">Opened</dt>
              <dd className="text-sm text-on-surface">{formatDateTime(caseData.created_at)}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-on-surface-variant">Status</dt>
              <dd className="text-sm text-on-surface">{caseData.status.replace(/_/g, ' ')}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-on-surface-variant">Linked alerts</dt>
              <dd className="text-sm font-semibold text-on-surface">{caseData.linked_alert_count}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-on-surface-variant">Flagged value</dt>
              <dd className="text-2xl font-semibold text-on-surface">
                {formatCurrency(caseData.flagged_value_total, caseData.currency)}
              </dd>
            </div>
          </dl>
        </section>

        {/* Investigation Notes */}
        <InvestigationNotesPanel caseId={caseId!} notes={notes} onSaveNote={handleSaveNote} />

        {/* Evidence Gap Card */}
        <article
          className="bg-warning-container border border-warning-container rounded-xl p-4 flex flex-col gap-3"
          aria-labelledby="h-gap"
        >
          <div className="flex gap-3 items-start">
            <svg className="w-6 h-6 flex-none text-warning" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
            </svg>
            <div>
              <h2 className="text-sm font-medium text-on-surface" id="h-gap">
                Evidence gap · Source of funds
              </h2>
              <p className="text-xs text-on-surface">Documentation is missing for TX-8821 (USD 48,500).</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => navigate(`/cases/${caseId}/information-requests`)}
            className="w-full min-h-[48px] px-6 py-3 rounded-xl bg-primary text-on-primary text-sm font-semibold"
          >
            Request information
          </button>
        </article>

        {/* Recent Activity */}
        {activeTab === 'activity' && (
          <section className="flex flex-col gap-3" id="activity" aria-labelledby="h-act">
            <h2 className="text-sm font-medium text-on-surface" id="h-act">
              Recent activity
            </h2>
            <ul className="flex flex-col" aria-label="Recent activity, read-only">
              {caseData.recent_activity.map((event) => (
                <li key={event.event_id} className="flex gap-3 py-2 border-b border-outline-variant last:border-0">
                  <span className="w-2 h-2 rounded-full bg-primary mt-1.5 flex-none" />
                  <div>
                    <p className="text-sm text-on-surface">{event.summary}</p>
                    <p className="text-xs text-on-surface-variant">
                      {formatDateTime(event.occurred_at)} · {event.actor_display}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Investigator Recommendation */}
        <RecommendationPanel
          caseId={caseId!}
          onSubmit={handleSubmitRecommendation}
          isBlocked={isRecommendationBlocked}
          blockerMessage={
            isRecommendationBlocked
              ? 'Resolve open information requests first.'
              : undefined
          }
        />
      </main>

      {/* Sticky Action Footer */}
      <div className="fixed bottom-20 left-0 right-0 bg-surface-container-high px-4 py-3 flex gap-3 border-t border-outline-variant">
        <button
          type="button"
          onClick={() => navigate(`/cases/${caseId}/information-requests`)}
          className="flex-1 min-h-[48px] px-6 py-3 rounded-xl bg-primary text-on-primary text-sm font-semibold"
        >
          Request information
        </button>
        <button
          type="button"
          className="flex-1 min-h-[48px] px-4 border border-outline rounded-xl bg-surface text-primary text-sm font-semibold"
        >
          Save note
        </button>
      </div>

      {/* Bottom Navigation */}
      <nav
        className="fixed bottom-0 left-0 right-0 bg-surface-container h-20 border-t border-outline-variant flex"
        aria-label="Primary"
      >
        <Link to="/alerts" className="flex-1 flex flex-col items-center justify-center gap-1 text-on-surface-variant">
          <span className="w-16 h-8 rounded-2xl flex items-center justify-center">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z" />
            </svg>
          </span>
          <span className="text-xs">Alerts</span>
        </Link>
        <Link
          to={`/cases/${caseId}`}
          className="flex-1 flex flex-col items-center justify-center gap-1 text-primary font-semibold"
          aria-current="page"
        >
          <span className="w-16 h-8 rounded-2xl bg-secondary-container flex items-center justify-center">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
            </svg>
          </span>
          <span className="text-xs">Cases</span>
        </Link>
      </nav>
    </div>
  );
}
