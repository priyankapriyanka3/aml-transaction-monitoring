// Review Handoff Page - wireframe_05
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AmlTopBar } from '../components/layout/AmlTopBar';
import { StickyActionFooter } from '../components/layout/StickyActionFooter';
import { ReadinessChecklistCard } from '../components/cases/ReadinessChecklistCard';
import { FourEyesSegregationCard } from '../components/cases/FourEyesSegregationCard';
import { apiClient } from '../lib/api-client';
import type { HandoffPackage, HandoffSubmitRequest } from '../types/handoff';

export function ReviewHandoffPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();

  const [handoffData, setHandoffData] = useState<HandoffPackage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOfficerId, setSelectedOfficerId] = useState<string>('');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Mock officers list - in production this would come from the API
  const availableOfficers = [
    { user_id: 'usr-002', display_name: 'Morgan Ellis', role: 'AML Officer' },
    { user_id: 'usr-003', display_name: 'Priya Nair', role: 'AML Officer' }
  ];

  useEffect(() => {
    loadHandoffData();
  }, [caseId]);

  async function loadHandoffData() {
    if (!caseId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.request<HandoffPackage>(`/cases/${caseId}/handoff`);
      setHandoffData(response);
      
      // Pre-select first available officer if none selected
      if (!selectedOfficerId && availableOfficers.length > 0) {
        setSelectedOfficerId(availableOfficers[0].user_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load handoff data');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmitHandoff() {
    if (!selectedOfficerId || !handoffData?.readiness.is_ready) return;

    try {
      setSubmitting(true);
      setError(null);

      const payload: HandoffSubmitRequest = {
        officer_user_id: selectedOfficerId
      };

      await apiClient.request(`/cases/${caseId}/handoff`, {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      // Success - navigate back to alerts
      navigate('/alerts');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit handoff');
    } finally {
      setSubmitting(false);
      setShowConfirmDialog(false);
    }
  }

  function handleNavigateBack() {
    navigate(`/cases/${caseId}/information-requests`);
  }

  const selectedOfficer = availableOfficers.find(o => o.user_id === selectedOfficerId);
  const isReady = handoffData?.readiness.is_ready || false;
  const unresolvedIssues = handoffData?.unresolved_issues || [];

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-[--background]">
        <AmlTopBar title="Loading..." subtitle="Review readiness" onBackClick={handleNavigateBack} />
        <main className="flex-1 p-4">
          <div className="animate-pulse space-y-4">
            <div className="h-32 bg-[--surface-variant] rounded-xl"></div>
            <div className="h-48 bg-[--surface-variant] rounded-xl"></div>
          </div>
        </main>
      </div>
    );
  }

  if (!handoffData) {
    return (
      <div className="min-h-screen flex flex-col bg-[--background]">
        <AmlTopBar title={caseId || 'Case'} subtitle="Review readiness" onBackClick={handleNavigateBack} />
        <main className="flex-1 p-4">
          <div className="bg-[--critical-container] text-[--on-surface] rounded-2xl p-4">
            <p className="text-sm">Failed to load handoff data</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[--background]">
      <AmlTopBar 
        title={handoffData.case_number}
        subtitle="Review readiness"
        eyebrow="TRANSFER REVIEW · 05 OF 05"
        onBackClick={handleNavigateBack}
      />

      <main className="flex-1 p-4 space-y-6 pb-32">
        {/* Decision Blocker Banner when not ready */}
        {!isReady && unresolvedIssues.some(issue => issue.includes('request')) && (
          <div 
            className="bg-[--warning-container] text-[--on-surface] rounded-2xl p-4 flex gap-3 items-start"
            role="status"
            aria-live="polite"
          >
            <svg className="w-6 h-6 flex-shrink-0 text-[--warning]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
            </svg>
            <div>
              <p className="font-medium text-sm leading-5">1 open request — decision blocked</p>
              <p className="text-xs leading-4 mt-1 text-[--on-surface-variant]">
                Approval, rejection and closure remain blocked while any request is open or overdue.
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-[--critical-container] text-[--on-surface] rounded-2xl p-4 flex gap-3 items-start">
            <svg className="w-6 h-6 flex-shrink-0 text-[--critical]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Readiness Checklist */}
        <ReadinessChecklistCard readiness={handoffData.readiness} />

        {/* Handoff Package Preview */}
        {isReady && (
          <section className="bg-[--surface-container-low] border border-[--surface-container-low] rounded-xl p-4 space-y-3">
            <div className="flex justify-between items-center gap-2">
              <h2 className="text-lg font-semibold">Handoff package preview</h2>
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs leading-4 font-medium bg-[--surface-variant] text-[--on-surface-variant]">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2z"/>
                </svg>
                What the officer receives
              </span>
            </div>

            <ul className="space-y-3" aria-label="Package contents">
              {/* Case Summary */}
              <li className="py-3 border-b border-[--outline-variant]/50">
                <p className="text-[11px] leading-[14px] font-semibold uppercase tracking-wider text-[--on-surface-variant]">Case</p>
                <p className="text-sm font-semibold leading-5 mt-1">{handoffData.case_number}</p>
                <p className="text-xs leading-4 text-[--on-surface-variant] mt-1">
                  {handoffData.linked_alerts.length} linked alert{handoffData.linked_alerts.length !== 1 ? 's' : ''}
                </p>
              </li>

              {/* Evidence */}
              {handoffData.key_evidence_summary.length > 0 && (
                <li className="py-3 border-b border-[--outline-variant]/50">
                  <p className="text-[11px] leading-[14px] font-semibold uppercase tracking-wider text-[--on-surface-variant]">Evidence and rule snapshot</p>
                  <p className="text-sm leading-5 mt-1">{handoffData.key_evidence_summary.join(' · ')}</p>
                </li>
              )}

              {/* Recommendation */}
              {handoffData.recommendation_outcome && (
                <li className="py-3 border-b border-[--outline-variant]/50">
                  <p className="text-[11px] leading-[14px] font-semibold uppercase tracking-wider text-[--on-surface-variant]">Recommendation</p>
                  <p className="text-sm leading-5 mt-1">{handoffData.findings_summary}</p>
                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs leading-4 font-medium bg-[--surface-variant] text-[--on-surface-variant] mt-2">
                    Recommendation — not a final decision
                  </span>
                </li>
              )}

              {/* Information Requests */}
              {handoffData.information_request_summary.length > 0 && (
                <li className="py-3">
                  <p className="text-[11px] leading-[14px] font-semibold uppercase tracking-wider text-[--on-surface-variant]">Information requests</p>
                  <p className="text-sm leading-5 mt-1">
                    {handoffData.information_request_summary.map(ir => ir.information_request_id).join(' · ')}
                  </p>
                </li>
              )}
            </ul>
          </section>
        )}

        {/* Unresolved Issues */}
        <section className="bg-[--surface] border border-[--outline-variant] rounded-xl p-4 space-y-2">
          <h2 className="font-medium text-sm leading-5">Unresolved issues</h2>
          {unresolvedIssues.length === 0 ? (
            <p className="text-sm leading-5">
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs leading-4 font-medium bg-[--success-container] text-[--on-success-container]">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                None
              </span>
            </p>
          ) : (
            <p className="text-sm leading-5">{unresolvedIssues.join(' · ')}</p>
          )}
        </section>

        {/* Four-Eyes Segregation Card */}
        <FourEyesSegregationCard 
          officers={availableOfficers}
          selectedOfficerId={selectedOfficerId}
          onSelectOfficer={setSelectedOfficerId}
        />
      </main>

      <StickyActionFooter>
        <div className="flex-1 space-y-2">
          <button
            onClick={() => setShowConfirmDialog(true)}
            disabled={!isReady || !selectedOfficerId || submitting}
            className="w-full min-h-[48px] px-6 rounded-xl font-semibold text-sm bg-[--primary] text-[--on-primary] disabled:opacity-38"
          >
            Share for officer review
          </button>
          <p className="text-xs leading-4 text-center text-[--on-surface-variant]">
            The officer receives this exact package. Final decision recording is not part of this release.
          </p>
        </div>
      </StickyActionFooter>

      {/* Confirmation Dialog */}
      {showConfirmDialog && selectedOfficer && (
        <div className="fixed inset-0 bg-[--scrim] flex items-center justify-center p-4 z-50">
          <div 
            className="bg-[--surface-container-high] rounded-[28px] p-6 max-w-sm w-full space-y-4"
            role="alertdialog"
            aria-labelledby="confirm-title"
            aria-describedby="confirm-desc"
          >
            <h3 id="confirm-title" className="text-lg font-semibold">
              Share {handoffData.case_number} with {selectedOfficer.display_name}?
            </h3>
            <p id="confirm-desc" className="text-sm text-[--on-surface-variant]">
              {selectedOfficer.display_name} receives this exact package and the case moves to Submitted for review. 
              You will no longer be able to edit it unless it is returned.
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowConfirmDialog(false)}
                className="min-h-[48px] px-3 rounded-xl font-semibold text-sm text-[--secondary] bg-transparent"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitHandoff}
                disabled={submitting}
                className="min-h-[48px] px-6 rounded-xl font-semibold text-sm bg-[--primary] text-[--on-primary] disabled:opacity-38"
              >
                {submitting ? 'Sharing...' : 'Share'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
