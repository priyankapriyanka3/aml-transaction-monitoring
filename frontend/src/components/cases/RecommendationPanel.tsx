import { useState } from 'react';
import { RecommendationRequest } from '../../types/case';

interface RecommendationPanelProps {
  caseId: string;
  onSubmit: (request: RecommendationRequest) => Promise<void>;
  isBlocked?: boolean;
  blockerMessage?: string;
}

export function RecommendationPanel({
  caseId,
  onSubmit,
  isBlocked = false,
  blockerMessage,
}: RecommendationPanelProps) {
  const [outcome, setOutcome] = useState<RecommendationRequest['recommendation_outcome'] | ''>('');
  const [findingsSummary, setFindingsSummary] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!outcome) {
      setError('Please select a recommendation outcome');
      return;
    }

    if (!findingsSummary.trim() || findingsSummary.trim().length < 50) {
      setError('Findings summary must be at least 50 characters');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');

      await onSubmit({
        recommendation_outcome: outcome,
        findings_summary: findingsSummary.trim(),
      });

      // Form will be cleared/disabled after successful submission
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit recommendation');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section
      className="bg-surface-container-low border border-primary rounded-xl p-4 flex flex-col gap-3"
      aria-labelledby="h-rec"
    >
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-on-surface" id="h-rec">
          Investigator recommendation
        </h2>
        <span className="inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium bg-surface-variant text-on-surface-variant">
          Not a final decision
        </span>
      </div>

      <p className="text-xs text-on-surface-variant">
        Your recommendation goes to an independent officer, who decides separately.
      </p>

      {/* Outcome Selection */}
      <div className="flex flex-col gap-2" role="radiogroup" aria-label="Recommendation outcome">
        <button
          type="button"
          onClick={() => setOutcome('NO_FURTHER_ACTION')}
          disabled={isBlocked}
          className={`min-h-[56px] px-3 flex items-center gap-3 rounded-xl border ${
            outcome === 'NO_FURTHER_ACTION'
              ? 'border-primary bg-primary-container'
              : 'border-outline-variant bg-surface'
          } disabled:opacity-38`}
          role="radio"
          aria-checked={outcome === 'NO_FURTHER_ACTION'}
        >
          <span className="w-5 h-5 rounded-full border-2 border-current flex items-center justify-center">
            {outcome === 'NO_FURTHER_ACTION' && <span className="w-2.5 h-2.5 rounded-full bg-primary" />}
          </span>
          <span className="text-sm">Recommend closure — activity explained</span>
        </button>

        <button
          type="button"
          onClick={() => setOutcome('SUBSTANTIATE')}
          disabled={isBlocked}
          className={`min-h-[56px] px-3 flex items-center gap-3 rounded-xl border ${
            outcome === 'SUBSTANTIATE'
              ? 'border-primary bg-primary-container'
              : 'border-outline-variant bg-surface'
          } disabled:opacity-38`}
          role="radio"
          aria-checked={outcome === 'SUBSTANTIATE'}
        >
          <span className="w-5 h-5 rounded-full border-2 border-current flex items-center justify-center">
            {outcome === 'SUBSTANTIATE' && <span className="w-2.5 h-2.5 rounded-full bg-primary" />}
          </span>
          <span className="font-semibold">Recommend further review</span>
        </button>

        <button
          type="button"
          onClick={() => setOutcome('ESCALATE_FOR_REVIEW')}
          disabled={isBlocked}
          className={`min-h-[56px] px-3 flex items-center gap-3 rounded-xl border ${
            outcome === 'ESCALATE_FOR_REVIEW'
              ? 'border-primary bg-primary-container'
              : 'border-outline-variant bg-surface'
          } disabled:opacity-38`}
          role="radio"
          aria-checked={outcome === 'ESCALATE_FOR_REVIEW'}
        >
          <span className="w-5 h-5 rounded-full border-2 border-current flex items-center justify-center">
            {outcome === 'ESCALATE_FOR_REVIEW' && <span className="w-2.5 h-2.5 rounded-full bg-primary" />}
          </span>
          <span className="text-sm">Recommend escalation for enhanced scrutiny</span>
        </button>
      </div>

      {/* Findings Summary */}
      <div className="flex flex-col gap-1">
        <label htmlFor="findings" className="text-xs font-medium text-on-surface-variant">
          Findings summary *
        </label>
        <textarea
          id="findings"
          value={findingsSummary}
          onChange={(e) => setFindingsSummary(e.target.value)}
          disabled={isBlocked}
          className={`w-full min-h-[112px] px-4 py-3 border rounded-xl bg-surface text-on-surface text-base resize-none disabled:opacity-38 ${
            error && findingsSummary.trim().length < 50 ? 'border-critical' : 'border-outline'
          }`}
          aria-required="true"
          aria-invalid={!!(error && findingsSummary.trim().length < 50)}
          placeholder="Summarize key findings (minimum 50 characters)"
        />
        <p className="text-xs text-on-surface-variant">{findingsSummary.length} / 2000</p>
      </div>

      {/* Blocker Message */}
      {isBlocked && blockerMessage && (
        <div className="bg-warning-container text-on-warning-container rounded-2xl p-4 flex gap-3" role="alert">
          <svg className="w-6 h-6 flex-none" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
          </svg>
          <div>
            <p className="text-sm font-medium">{blockerMessage}</p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <p className="text-xs text-critical" role="alert">
          {error}
        </p>
      )}

      {/* Submit Button */}
      <button
        type="button"
        onClick={handleSubmit}
        disabled={isBlocked || isSubmitting || !outcome || findingsSummary.trim().length < 50}
        className="w-full min-h-[48px] px-6 py-3 rounded-xl bg-primary text-on-primary text-sm font-semibold disabled:opacity-38"
      >
        {isSubmitting ? 'Submitting...' : 'Submit recommendation for review'}
      </button>

      <p className="text-xs text-on-surface-variant">Opens the review handoff (wireframe 5).</p>
    </section>
  );
}
