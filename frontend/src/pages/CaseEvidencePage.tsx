import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../lib/api-client';
import { EvidencePackage } from '../types/evidence';
import { CustomerRiskPanel } from '../components/evidence/CustomerRiskPanel';
import { AccountRelationshipList } from '../components/evidence/AccountRelationshipList';
import { TransactionTimelineTable } from '../components/evidence/TransactionTimelineTable';
import { RuleEvaluationOutcomeRow } from '../components/evidence/RuleEvaluationOutcomeRow';

export function CaseEvidencePage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();

  const [evidence, setEvidence] = useState<EvidencePackage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadEvidence = async () => {
    if (!caseId) return;
    
    try {
      setLoading(true);
      setError('');
      const response = await apiClient.get<EvidencePackage>(`/cases/${caseId}/evidence-package`);
      setEvidence(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load evidence');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvidence();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !evidence) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="bg-critical-container text-on-critical-container rounded-2xl p-4 max-w-md flex flex-col gap-4">
          <div className="flex gap-3 items-start">
            <svg className="w-6 h-6 flex-none text-critical" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
            </svg>
            <div>
              <h3 className="text-sm font-medium">Evidence could not be loaded</h3>
              <p className="text-xs">{error || 'Case not found'}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={loadEvidence}
            className="min-h-[48px] px-6 py-3 rounded-xl bg-primary text-on-primary text-sm font-semibold flex items-center justify-center gap-2"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M17.65 6.35A7.958 7.958 0 0 0 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" />
            </svg>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const linkedAlertCount = evidence.transactions.filter((tx) => tx.linked_alert_id).length;

  return (
    <div className="min-h-screen bg-background pb-32">
      {/* Top App Bar */}
      <header className="bg-surface min-h-[64px] flex items-center gap-1 px-1 border-b border-outline-variant">
        <button
          onClick={() => navigate(`/cases/${caseId}`)}
          className="w-12 h-12 flex items-center justify-center rounded-full text-primary"
          aria-label={`Navigate up to case ${caseId}`}
        >
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
          </svg>
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="text-lg font-semibold text-on-surface">{caseId} · Evidence</h1>
          <p className="text-xs text-on-surface-variant">{evidence.customer.customer_name}</p>
        </div>
        {evidence.evidence_locked_for_review && (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium bg-info-container text-on-info-container">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zM9 8V6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9z" />
            </svg>
            Evidence set v1 · preserved
          </span>
        )}
      </header>

      {/* Secondary Tabs */}
      <nav
        className="bg-surface border-b border-outline-variant flex overflow-x-auto"
        role="tablist"
        aria-label="Case sections"
      >
        <Link
          to={`/cases/${caseId}`}
          role="tab"
          aria-selected="false"
          className="flex-none min-h-[48px] px-3 text-sm border-b-[3px] text-on-surface-variant border-transparent"
        >
          Overview
        </Link>
        <Link
          to={`/cases/${caseId}/evidence`}
          role="tab"
          aria-selected="true"
          className="flex-none min-h-[48px] px-3 text-sm border-b-[3px] text-primary font-semibold border-primary"
        >
          Linked alerts ({linkedAlertCount})
        </Link>
        <Link
          to={`/cases/${caseId}/information-requests`}
          role="tab"
          aria-selected="false"
          className="flex-none min-h-[48px] px-3 text-sm border-b-[3px] text-on-surface-variant border-transparent"
        >
          Requests
        </Link>
        <a
          href={`#activity`}
          role="tab"
          aria-selected="false"
          className="flex-none min-h-[48px] px-3 text-sm border-b-[3px] text-on-surface-variant border-transparent"
        >
          Activity
        </a>
      </nav>

      {/* Main Content */}
      <main className="px-4 py-6 flex flex-col gap-6">
        {/* Customer Risk Context */}
        <CustomerRiskPanel customer={evidence.customer} />

        {/* Account Relationships */}
        <AccountRelationshipList accounts={evidence.accounts} />

        {/* Transaction Evidence Timeline */}
        <TransactionTimelineTable transactions={evidence.transactions} />

        {/* Rule-Hit Rationale */}
        <section
          className="bg-surface border border-outline-variant rounded-xl p-4 flex flex-col gap-3"
          aria-labelledby="h-rules"
        >
          <h2 className="text-lg font-semibold text-on-surface" id="h-rules">
            Rule-hit rationale
          </h2>

          <div
            className="bg-info-container rounded-2xl p-4 flex gap-3"
            role="note"
          >
            <svg className="w-6 h-6 flex-none text-info" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" />
            </svg>
            <p className="text-xs text-on-surface">
              Historical versions used at evaluation — not the latest rules.
            </p>
          </div>

          <ul>
            {evidence.rule_evaluations.map((evaluation) => (
              <RuleEvaluationOutcomeRow key={evaluation.rule_evaluation_id} evaluation={evaluation} />
            ))}
          </ul>
        </section>
      </main>

      {/* Sticky Action Footer */}
      <div className="fixed bottom-20 left-0 right-0 bg-surface-container-high px-4 py-3 flex gap-3 border-t border-outline-variant">
        <button
          type="button"
          onClick={() => navigate(`/cases/${caseId}`)}
          className="flex-1 min-h-[48px] px-6 py-3 rounded-xl bg-primary text-on-primary text-sm font-semibold"
        >
          Back to case
        </button>
        <button
          type="button"
          onClick={() => navigate(`/cases/${caseId}/information-requests`)}
          className="flex-1 min-h-[48px] px-4 border border-outline rounded-xl bg-surface text-primary text-sm font-semibold"
        >
          Request information
        </button>
      </div>

      {/* Bottom Navigation - Fixed to use Link for Cases */}
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
