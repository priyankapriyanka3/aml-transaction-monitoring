import { Alert } from '../../types/alert';
import { formatCurrency, formatDateTime, cn } from '../../lib/utils';

interface HeroAlertCardProps {
  alert: Alert;
  onAssign: (alertId: string) => void;
  onCreateCase: (alertId: string) => void;
  isAssigning?: boolean;
  currentUserId?: string;
}

export function HeroAlertCard({
  alert,
  onAssign,
  onCreateCase,
  isAssigning = false,
  currentUserId,
}: HeroAlertCardProps) {
  const isAssigned = !!alert.assigned_user_id;
  const isOwnedByUser = alert.assigned_user_id === currentUserId;

  const priorityBadgeClass = cn(
    'inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium',
    {
      'bg-critical-container text-on-critical-container': alert.priority === 'CRITICAL',
      'bg-warning-container text-on-warning-container': alert.priority === 'HIGH',
      'bg-info-container text-on-info-container': alert.priority === 'MEDIUM',
      'bg-surface-variant text-on-surface-variant': alert.priority === 'LOW',
    }
  );

  const statusBadgeClass = 'inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium bg-info-container text-on-info-container';

  return (
    <article
      className="bg-surface border-[1.5px] border-hero-stroke rounded-xl p-4 flex flex-col gap-3"
      aria-label={`Alert ${alert.alert_id}, ${alert.priority} priority, Score ${alert.risk_score}`}
    >
      {/* Header: Alert ID + Priority Badge */}
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-lg font-semibold text-on-surface">{alert.alert_id}</h3>
        <span className={priorityBadgeClass}>
          {alert.priority} · Score {alert.risk_score}
        </span>
      </div>

      {/* Transaction ID + Timestamp */}
      <p className="text-sm text-on-surface-variant">
        Transaction {alert.transaction_id} · evaluated {formatDateTime(alert.created_at)}
      </p>

      {/* Transaction Amount + Corridor */}
      <div className="flex items-center justify-between gap-2">
        <p className="text-2xl font-semibold text-on-surface">
          {alert.transaction_currency && alert.transaction_amount
            ? formatCurrency(alert.transaction_amount, alert.transaction_currency)
            : 'N/A'}
        </p>
        {alert.generation && (
          <span className="inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium bg-surface-variant text-on-surface-variant">
            {alert.generation}
          </span>
        )}
      </div>

      {/* Customer */}
      <p className="text-sm text-on-surface">
        Customer: {alert.customer_name || 'N/A'} ({alert.customer_id})
      </p>

      {/* Status + Assignment */}
      <div className="flex flex-wrap items-center gap-2">
        <span className={statusBadgeClass}>Status: {alert.status.replace(/_/g, ' ')}</span>
        {isAssigned && (
          <span className="inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium bg-surface-variant text-on-surface-variant">
            {alert.assigned_user_name || 'Assigned'}
          </span>
        )}
      </div>

      {/* Rule Matches */}
      <p className="text-xs text-on-surface-variant">
        {alert.matched_rule_codes_json ? JSON.parse(alert.matched_rule_codes_json).length : 0} rule(s) matched
      </p>

      {/* Actions */}
      {!isAssigned && (
        <>
          <button
            type="button"
            onClick={() => onAssign(alert.alert_id)}
            disabled={isAssigning}
            className="w-full min-h-[48px] px-6 py-3 rounded-xl bg-primary text-on-primary text-sm font-semibold disabled:opacity-38"
          >
            {isAssigning ? 'Assigning...' : 'Assign to me'}
          </button>
          <button
            type="button"
            disabled
            className="w-full min-h-[48px] px-6 py-3 rounded-xl border border-outline bg-surface text-primary text-sm font-semibold opacity-38"
          >
            Create case
          </button>
          <p className="text-xs text-on-surface-variant">
            Create case unlocks after you assign this alert to yourself.
          </p>
        </>
      )}

      {isAssigned && isOwnedByUser && (
        <>
          <button
            type="button"
            onClick={() => onCreateCase(alert.alert_id)}
            className="w-full min-h-[48px] px-6 py-3 rounded-xl bg-primary text-on-primary text-sm font-semibold"
          >
            Create case
          </button>
          <p className="text-xs text-on-surface-variant">
            Create case keeps the alert ID, score and your triage rationale.
          </p>
        </>
      )}

      {isAssigned && !isOwnedByUser && (
        <p className="text-xs text-on-surface-variant">
          Assignment: {alert.assigned_user_name} · {formatDateTime(alert.updated_at)}
        </p>
      )}
    </article>
  );
}
