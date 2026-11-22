// Information Requests Page - wireframe_04
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AmlTopBar } from '../components/layout/AmlTopBar';
import { StickyActionFooter } from '../components/layout/StickyActionFooter';
import { DecisionBlockerBanner } from '../components/information-requests/DecisionBlockerBanner';
import { InformationRequestForm } from '../components/information-requests/InformationRequestForm';
import { InformationRequestHistoryList } from '../components/information-requests/InformationRequestHistoryList';
import { apiClient } from '../lib/api-client';
import type { InformationRequest, RecordResponseRequest } from '../types/information-request';
import type { CaseOverview } from '../types';

export function InformationRequestsPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();

  const [caseData, setCaseData] = useState<CaseOverview | null>(null);
  const [requests, setRequests] = useState<InformationRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(null);
  const [showNewRequestForm, setShowNewRequestForm] = useState(false);
  const [responseFormDirty, setResponseFormDirty] = useState(false);

  // Response form state
  const [responseSummary, setResponseSummary] = useState('');
  const [receivedDate, setReceivedDate] = useState('');
  const [responseChannel, setResponseChannel] = useState('');

  useEffect(() => {
    loadData();
  }, [caseId]);

  useEffect(() => {
    // Handle back button with unsaved changes
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (responseFormDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [responseFormDirty]);

  async function loadData() {
    if (!caseId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const [caseResponse, requestsResponse] = await Promise.all([
        apiClient.request<CaseOverview>(`/cases/${caseId}`),
        apiClient.request<InformationRequest[]>(`/information-requests?case_id=${caseId}`)
      ]);
      
      setCaseData(caseResponse);
      setRequests(requestsResponse);
      
      // Auto-select first open request
      const openRequest = requestsResponse.find((r: InformationRequest) => r.status === 'OPEN');
      if (openRequest) {
        setSelectedRequestId(openRequest.information_request_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  async function handleRecordResponse() {
    if (!selectedRequestId || !responseSummary.trim() || !receivedDate) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      const payload: RecordResponseRequest = {
        response_summary: responseSummary,
        received_at: new Date(receivedDate).toISOString(),
        response_channel: responseChannel || 'EMAIL'
      };

      await apiClient.request(`/information-requests/${selectedRequestId}/record-response`, {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      setResponseFormDirty(false);
      setResponseSummary('');
      setReceivedDate('');
      setResponseChannel('');
      setSelectedRequestId(null);
      
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to record response');
    }
  }

  function handleNavigateBack() {
    if (responseFormDirty) {
      const confirmed = window.confirm(
        'Discard unsaved response?\n\nYour response summary has not been recorded. Going back will lose it.'
      );
      if (!confirmed) return;
    }
    navigate(`/cases/${caseId}`);
  }

  function handleResponseSummaryChange(value: string) {
    setResponseSummary(value);
    setResponseFormDirty(value.trim().length > 0);
  }

  const selectedRequest = requests.find(r => r.information_request_id === selectedRequestId);
  const hasBlocker = caseData && (
    caseData.open_information_request_count > 0 ||
    caseData.overdue_information_request_count > 0
  );

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-[--background]">
        <AmlTopBar title={caseId || 'Loading...'} subtitle="Information requests" onBackClick={handleNavigateBack} />
        <main className="flex-1 p-4">
          <div className="animate-pulse space-y-4">
            <div className="h-20 bg-[--surface-variant] rounded-xl"></div>
            <div className="h-32 bg-[--surface-variant] rounded-xl"></div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[--background]">
      <AmlTopBar 
        title={caseData?.case_number || caseId || 'Case'} 
        subtitle="Information requests" 
        onBackClick={handleNavigateBack}
      />

      <main className="flex-1 p-4 space-y-6">
        {hasBlocker && (
          <DecisionBlockerBanner 
            openCount={caseData.open_information_request_count}
            overdueCount={caseData.overdue_information_request_count}
          />
        )}

        {error && (
          <div className="bg-[--critical-container] text-[--on-surface] rounded-2xl p-4 flex gap-3 items-start">
            <svg className="w-6 h-6 flex-shrink-0 text-[--critical]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
            <div>
              <p className="font-medium text-sm leading-5">Error</p>
              <p className="text-xs leading-4 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Request List */}
        <section className="space-y-3">
          <h2 className="text-lg font-semibold leading-6">Requests</h2>
          
          {requests.length === 0 ? (
            <div className="bg-[--surface] border border-[--outline-variant] rounded-xl p-6 text-center">
              <svg className="w-12 h-12 mx-auto text-[--on-surface-variant]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 3H4.99c-1.11 0-1.98.89-1.98 2L3 19c0 1.1.88 2 1.99 2H19c1.1 0 2-.9 2-2V5c0-1.11-.9-2-2-2zm0 12h-4c0 1.66-1.35 3-3 3s-3-1.34-3-3H4.99V5H19v10z"/>
              </svg>
              <h3 className="mt-2 text-lg font-semibold">No requests on this case yet</h3>
              <p className="mt-1 text-sm text-[--on-surface-variant]">Send the first request to ask for missing evidence.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {requests.map(req => (
                <article 
                  key={req.information_request_id}
                  className={`bg-[--surface] border rounded-xl p-4 space-y-3 cursor-pointer transition-colors ${
                    selectedRequestId === req.information_request_id 
                      ? 'border-[--hero-stroke] border-[1.5px]' 
                      : 'border-[--outline-variant]'
                  }`}
                  onClick={() => req.status === 'OPEN' && setSelectedRequestId(req.information_request_id)}
                >
                  <div className="flex justify-between items-center gap-2">
                    <h3 className="text-lg font-semibold">{req.information_request_id}</h3>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs leading-4 font-medium ${
                      req.is_overdue 
                        ? 'bg-[--critical-container] text-[--on-critical-container]' 
                        : req.status === 'RESPONDED' 
                        ? 'bg-[--success-container] text-[--on-success-container]'
                        : 'bg-[--warning-container] text-[--on-warning-container]'
                    }`}>
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        {req.is_overdue ? (
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                        ) : req.status === 'RESPONDED' ? (
                          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                        ) : (
                          <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                        )}
                      </svg>
                      {req.is_overdue ? `Overdue · ${Math.abs(req.days_remaining || 0)} days` : 
                       req.status === 'RESPONDED' ? 'Fulfilled · On time' : 
                       `Open · ${req.days_remaining} day${req.days_remaining !== 1 ? 's' : ''} remaining`}
                    </span>
                  </div>
                  
                  <p className="text-sm leading-5">{req.requested_summary}</p>
                  
                  <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-xs leading-4">
                    <dt className="text-[--on-surface-variant]">Due</dt>
                    <dd>{new Date(req.due_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}</dd>
                    <dt className="text-[--on-surface-variant]">Target</dt>
                    <dd>{req.recipient_channel}</dd>
                    {req.status === 'RESPONDED' && req.response_received_at && (
                      <>
                        <dt className="text-[--on-surface-variant]">Received</dt>
                        <dd>{new Date(req.response_received_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}</dd>
                      </>
                    )}
                  </dl>
                </article>
              ))}
            </div>
          )}
        </section>

        {/* Response Form */}
        {selectedRequest && selectedRequest.status === 'OPEN' && (
          <section className="bg-[--surface] border border-[--outline-variant] rounded-xl p-4 space-y-3">
            <h2 className="text-lg font-semibold">Record response · {selectedRequest.information_request_id}</h2>
            
            <div className="space-y-1">
              <label htmlFor="response-summary" className="block text-xs leading-4 font-medium text-[--on-surface-variant]">
                Response summary *
              </label>
              <textarea
                id="response-summary"
                value={responseSummary}
                onChange={e => handleResponseSummaryChange(e.target.value)}
                className="w-full min-h-[112px] border border-[--outline] rounded-xl bg-[--surface] p-3 text-base leading-6 resize-none focus:outline-none focus:border-2 focus:border-[--primary]"
                placeholder="Describe the response received"
                required
              />
              <p className="text-xs leading-3.5 font-semibold text-[--on-surface-variant]">
                Required · {responseSummary.length} / 2000
              </p>
            </div>

            <div className="space-y-1">
              <label htmlFor="received-date" className="block text-xs leading-4 font-medium text-[--on-surface-variant]">
                Received date *
              </label>
              <input
                type="date"
                id="received-date"
                value={receivedDate}
                onChange={e => setReceivedDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className="w-full min-h-[56px] border border-[--outline] rounded-xl bg-[--surface] px-4 text-base leading-6 focus:outline-none focus:border-2 focus:border-[--primary]"
                required
              />
              <p className="text-xs leading-3.5 font-semibold text-[--on-surface-variant]">
                Future dates cannot be selected.
              </p>
            </div>

            <div className="space-y-1">
              <label htmlFor="response-channel" className="block text-xs leading-4 font-medium text-[--on-surface-variant]">
                Channel
              </label>
              <select
                id="response-channel"
                value={responseChannel}
                onChange={e => setResponseChannel(e.target.value)}
                className="w-full min-h-[56px] border border-[--outline] rounded-xl bg-[--surface] px-4 text-base leading-6 focus:outline-none focus:border-2 focus:border-[--primary]"
              >
                <option value="">Select channel</option>
                <option value="EMAIL">Email</option>
                <option value="PORTAL">Portal</option>
                <option value="OPERATIONS_QUEUE">Operations queue</option>
              </select>
            </div>
          </section>
        )}

        {/* Request History Timeline */}
        <InformationRequestHistoryList requests={requests} />
      </main>

      <StickyActionFooter>
        <button
          onClick={handleRecordResponse}
          disabled={!selectedRequest || !responseSummary.trim() || !receivedDate}
          className="flex-1 min-h-[48px] px-6 rounded-xl font-semibold text-sm bg-[--primary] text-[--on-primary] disabled:opacity-38"
        >
          Record response
        </button>
        <button
          onClick={() => setShowNewRequestForm(true)}
          className="flex-1 min-h-[48px] px-6 rounded-xl font-semibold text-sm bg-[--surface] text-[--primary] border border-[--outline]"
        >
          New request
        </button>
      </StickyActionFooter>

      {showNewRequestForm && (
        <InformationRequestForm 
          caseId={caseId!}
          onClose={() => setShowNewRequestForm(false)}
          onSuccess={() => {
            setShowNewRequestForm(false);
            loadData();
          }}
        />
      )}
    </div>
  );
}
