// Information Request Form - modal for creating new requests

import { useState } from 'react';
import { apiClient } from '../../lib/api-client';
import type { InformationRequestCreateRequest } from '../../types/information-request';

interface InformationRequestFormProps {
  caseId: string;
  onClose: () => void;
  onSuccess: () => void;
}

export function InformationRequestForm({ caseId, onClose, onSuccess }: InformationRequestFormProps) {
  const [requestedSummary, setRequestedSummary] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [recipientChannel, setRecipientChannel] = useState('EMAIL');
  const [rationale, setRationale] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);

  const isValid = requestedSummary.trim().length >= 10 && 
                  rationale.trim().length >= 10 && 
                  dueDate.length > 0;

  async function handleSubmit() {
    if (!isValid) return;

    try {
      setSubmitting(true);
      setError(null);

      const payload: InformationRequestCreateRequest = {
        case_id: caseId,
        recipient_channel: recipientChannel,
        requested_summary: requestedSummary,
        rationale: rationale,
        due_at: new Date(dueDate).toISOString()
      };

      await apiClient.request('/information-requests', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create request');
    } finally {
      setSubmitting(false);
      setShowConfirm(false);
    }
  }

  const minDate = new Date();
  minDate.setDate(minDate.getDate() + 1);
  const minDateStr = minDate.toISOString().split('T')[0];

  if (showConfirm) {
    return (
      <div className="fixed inset-0 bg-[--scrim] flex items-center justify-center p-4 z-50">
        <div 
          className="bg-[--surface-container-high] rounded-[28px] p-6 max-w-sm w-full space-y-4"
          role="alertdialog"
          aria-labelledby="confirm-title"
          aria-describedby="confirm-desc"
        >
          <h3 id="confirm-title" className="text-lg font-semibold">
            Send information request?
          </h3>
          <p id="confirm-desc" className="text-sm text-[--on-surface-variant]">
            Due {new Date(dueDate).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}. 
            Case {caseId} will move to Pending information and decision actions stay blocked until the response is recorded.
          </p>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setShowConfirm(false)}
              className="min-h-[48px] px-3 rounded-xl font-semibold text-sm text-[--secondary] bg-transparent"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="min-h-[48px] px-6 rounded-xl font-semibold text-sm bg-[--primary] text-[--on-primary] disabled:opacity-38"
            >
              {submitting ? 'Sending...' : 'Confirm'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-[--scrim] flex items-end z-50" onClick={onClose}>
      <div 
        className="bg-[--surface-container] rounded-t-[28px] p-4 w-full max-h-[90vh] overflow-y-auto space-y-4"
        role="dialog"
        aria-labelledby="form-title"
        onClick={e => e.stopPropagation()}
      >
        <div className="w-8 h-1 bg-[--outline] rounded-full mx-auto"></div>
        
        <h2 id="form-title" className="text-lg font-semibold">New information request</h2>

        {error && (
          <div className="bg-[--critical-container] text-[--on-surface] rounded-2xl p-4 flex gap-3 items-start">
            <svg className="w-6 h-6 flex-shrink-0 text-[--critical]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
            <p className="text-sm">{error}</p>
          </div>
        )}

        <div className="space-y-1">
          <label htmlFor="requested-summary" className="block text-xs leading-4 font-medium text-[--on-surface-variant]">
            Information requested * (describe the information or documents needed)
          </label>
          <textarea
            id="requested-summary"
            value={requestedSummary}
            onChange={e => setRequestedSummary(e.target.value)}
            className={`w-full min-h-[112px] border rounded-xl bg-[--surface] p-3 text-base leading-6 resize-none focus:outline-none focus:border-2 ${
              requestedSummary.length > 0 && requestedSummary.length < 10 
                ? 'border-[--critical] focus:border-[--critical]' 
                : 'border-[--outline] focus:border-[--primary]'
            }`}
            required
          />
          {requestedSummary.length > 0 && requestedSummary.length < 10 && (
            <p className="text-xs font-semibold text-[--critical]">Summary must be at least 10 characters.</p>
          )}
        </div>

        <div className="space-y-1">
          <label htmlFor="due-date" className="block text-xs leading-4 font-medium text-[--on-surface-variant]">
            Due date *
          </label>
          <input
            type="date"
            id="due-date"
            value={dueDate}
            onChange={e => setDueDate(e.target.value)}
            min={minDateStr}
            className={`w-full min-h-[56px] border rounded-xl bg-[--surface] px-4 text-base leading-6 focus:outline-none focus:border-2 ${
              dueDate.length === 0 
                ? 'border-[--outline] focus:border-[--primary]'
                : 'border-[--outline] focus:border-[--primary]'
            }`}
            required
          />
          {dueDate.length === 0 && (
            <p className="text-xs font-semibold text-[--on-surface-variant]">Due date is required.</p>
          )}
        </div>

        <div className="space-y-1">
          <label htmlFor="recipient-channel" className="block text-xs leading-4 font-medium text-[--on-surface-variant]">
            Target (optional)
          </label>
          <select
            id="recipient-channel"
            value={recipientChannel}
            onChange={e => setRecipientChannel(e.target.value)}
            className="w-full min-h-[56px] border border-[--outline] rounded-xl bg-[--surface] px-4 text-base leading-6 focus:outline-none focus:border-2 focus:border-[--primary]"
          >
            <option value="EMAIL">Email</option>
            <option value="PORTAL">Customer portal</option>
            <option value="OPERATIONS_QUEUE">Operations queue</option>
          </select>
        </div>

        <div className="space-y-1">
          <label htmlFor="rationale" className="block text-xs leading-4 font-medium text-[--on-surface-variant]">
            Reason *
          </label>
          <textarea
            id="rationale"
            value={rationale}
            onChange={e => setRationale(e.target.value)}
            className={`w-full min-h-[112px] border rounded-xl bg-[--surface] p-3 text-base leading-6 resize-none focus:outline-none focus:border-2 ${
              rationale.length > 0 && rationale.length < 10 
                ? 'border-[--critical] focus:border-[--critical]' 
                : 'border-[--outline] focus:border-[--primary]'
            }`}
            placeholder="Explain why this information is needed"
            required
          />
          {rationale.length > 0 && rationale.length < 10 && (
            <p className="text-xs font-semibold text-[--critical]">Reason must be at least 10 characters.</p>
          )}
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <button
            onClick={onClose}
            className="min-h-[48px] px-3 rounded-xl font-semibold text-sm text-[--secondary] bg-transparent"
          >
            Cancel
          </button>
          <button
            onClick={() => setShowConfirm(true)}
            disabled={!isValid || submitting}
            className="min-h-[48px] px-6 rounded-xl font-semibold text-sm bg-[--primary] text-[--on-primary] disabled:opacity-38"
          >
            Send request
          </button>
        </div>
      </div>
    </div>
  );
}
