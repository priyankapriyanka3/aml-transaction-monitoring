import { RuleEvaluation } from '../../types/evidence';
import { cn } from '../../lib/utils';

interface RuleEvaluationOutcomeRowProps {
  evaluation: RuleEvaluation;
}

export function RuleEvaluationOutcomeRow({ evaluation }: RuleEvaluationOutcomeRowProps) {
  const outcomeBadgeClass = cn(
    'inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium',
    {
      'bg-critical-container text-on-critical-container': evaluation.outcome === 'MATCH',
      'bg-success-container text-on-success-container': evaluation.outcome === 'PASS',
    }
  );

  const outcomeIcon =
    evaluation.outcome === 'MATCH' ? (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
      </svg>
    ) : (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
      </svg>
    );

  return (
    <li className="py-3 border-b border-outline-variant last:border-0 min-h-[72px] flex flex-col gap-1">
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-semibold text-on-surface">
          {evaluation.rule_name} · {evaluation.rule_version}
        </p>
        <span className={outcomeBadgeClass}>
          {outcomeIcon}
          {evaluation.outcome}
        </span>
      </div>
      <p className="text-xs text-on-surface-variant">{evaluation.threshold_explanation}</p>
    </li>
  );
}
