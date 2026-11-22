import { useState } from 'react';
import { TriageDispositionRequest } from '../../types/alert';

interface TriageDispositionModalProps {
  alertId: string;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (request: TriageDispositionRequest) => Promise<void>;
}

export function TriageDispositionModal({
  alertId,
  isOpen,
  onClose,
  onSubmit,
}: TriageDispositionModalProps) {
  const [outcome, setOutcome] = useState<TriageDispositionRequest['outcome'] | ''>('');
  const [rationale, setRationale] = useState('');
  const [existingCaseId, setExistingCaseId] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!outcome) {
      setError('Please select an outcome');
      return;
    }

    if (!rationale || rationale.trim().length < 10) {
      setError('Rationale must be at least 10 characters');
      return;
    }

    if (outcome === 'MERGE_EXISTING_CASE' && !existingCaseId.trim()) {
      setError('Existing case ID required when merging');
      return;
    }

    try {
      setIsSubmitting(true);
      await onSubmit({
        outcome,
        rationale: rationale.trim(),
        existing_case_id: outcome === 'MERGE_EXISTING_CASE' ? existingCaseId.trim() : undefined,
      });
      // Reset form and close
      setOutcome('');
      setRationale('');
      setExistingCaseId('');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save disposition');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setOutcome('');
    setRationale('');
    setExistingCaseId('');
    setError('');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end bg-scrim" onClick={handleCancel}>
      <div
        className="w-full max-w-md mx-auto bg-surface-container rounded-t-[28px] p-4 flex flex-col gap-4 animate-slide-up"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="triage-title"
      >
        {/* Drag Handle */}
        <div className="w-8 h-1 mx-auto bg-outline rounded-full" />

        <h2 id="triage-title" className="text-lg font-semibold text-on-surface">
          Triage alert {alertId}
        </h2>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Outcome Selection */}
          <div className="flex flex-col gap-2" role="radiogroup" aria-label="Triage outcome">
            <button
              type="button"
              onClick={() => setOutcome('INVESTIGATE')}
              className={`min-h-[56px] px-3 flex items-center gap-3 rounded-xl border ${
                outcome === 'INVESTIGATE'
                  ? 'border-primary bg-primary-container'
                  : 'border-outline-variant bg-surface'
              }`}
              role="radio"
              aria-checked={outcome === 'INVESTIGATE'}
            >
              <span className="w-5 h-5 rounded-full border-2 border-current flex items-center justify-center">
                {outcome === 'INVESTIGATE' && <span className="w-2.5 h-2.5 rounded-full bg-primary" />}
              </span>
              <span className="font-semibold">Escalate to case</span>
            </button>

            <button
              type="button"
              onClick={() => setOutcome('CLOSE_NON_ACTIONABLE')}
              className={`min-h-[56px] px-3 flex items-center gap-3 rounded-xl border ${
                outcome === 'CLOSE_NON_ACTIONABLE'
                  ? 'border-primary bg-primary-container'
                  : 'border-outline-variant bg-surface'
              }`}
              role="radio"
              aria-checked={outcome === 'CLOSE_NON_ACTIONABLE'}
            >
              <span className="w-5 h-5 rounded-full border-2 border-current flex items-center justify-center">
                {outcome === 'CLOSE_NON_ACTIONABLE' && <span className="w-2.5 h-2.5 rounded-full bg-primary" />}
              </span>
              <span className="text-sm">Close — false positive</span>
            </button>

            <button
              type="button"
              onClick={() => setOutcome('MERGE_EXISTING_CASE')}
              className={`min-h-[56px] px-3 flex items-center gap-3 rounded-xl border ${
                outcome === 'MERGE_EXISTING_CASE'
                  ? 'border-primary bg-primary-container'
                  : 'border-outline-variant bg-surface'
              }`}
              role="radio"
              aria-checked={outcome === 'MERGE_EXISTING_CASE'}
            >
              <span className="w-5 h-5 rounded-full border-2 border-current flex items-center justify-center">
                {outcome === 'MERGE_EXISTING_CASE' && <span className="w-2.5 h-2.5 rounded-full bg-primary" />}
              </span>
              <span className="text-sm">Link to existing case</span>
            </button>
          </div>

          {/* Existing Case ID Input */}
          {outcome === 'MERGE_EXISTING_CASE' && (
            <div className="flex flex-col gap-1">
              <label htmlFor="existing-case-id" className="text-xs font-medium text-on-surface-variant">
                Existing case ID
              </label>
              <input
                type="text"
                id="existing-case-id"
                value={existingCaseId}
                onChange={(e) => setExistingCaseId(e.target.value)}
                className="w-full min-h-[56px] px-4 border border-outline rounded-xl bg-surface text-on-surface text-base"
                placeholder="CS-XXX"
              />
            </div>
          )}

          {/* Rationale Textarea */}
          <div className="flex flex-col gap-1">
            <label htmlFor="rationale" className="text-xs font-medium text-on-surface-variant">
              Rationale *
            </label>
            <textarea
              id="rationale"
              value={rationale}
              onChange={(e) => setRationale(e.target.value)}
              className={`w-full min-h-[112px] px-4 py-3 border rounded-xl bg-surface text-on-surface text-base resize-none ${
                error && rationale.trim().length < 10 ? 'border-critical' : 'border-outline'
              }`}
              aria-required="true"
              aria-invalid={!!(error && rationale.trim().length < 10)}
              placeholder="Explain your triage decision (minimum 10 characters)"
            />
            <p className="text-xs text-on-surface-variant">
              Required. Stored with your user ID, role and UTC time.
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <p className="text-xs text-critical" role="alert">
              {error}
            </p>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={handleCancel}
              className="min-h-[48px] px-3 text-secondary text-sm font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !outcome || rationale.trim().length < 10}
              className="min-h-[48px] px-6 rounded-xl bg-primary text-on-primary text-sm font-semibold disabled:opacity-38"
            >
              {isSubmitting ? 'Saving...' : 'Save disposition'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
