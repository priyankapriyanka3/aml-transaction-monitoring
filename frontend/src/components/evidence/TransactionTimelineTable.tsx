import { useState } from 'react';
import { TransactionEvidence } from '../../types/evidence';
import { formatDateTime, formatCurrency, cn } from '../../lib/utils';

interface TransactionTimelineTableProps {
  transactions: TransactionEvidence[];
}

type SortBy = 'date' | 'amount' | 'alert';
type SortDirection = 'asc' | 'desc';

export function TransactionTimelineTable({ transactions }: TransactionTimelineTableProps) {
  const [sortBy, setSortBy] = useState<SortBy>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (field: SortBy) => {
    if (sortBy === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortDirection('desc');
    }
  };

  const sortedTransactions = [...transactions].sort((a, b) => {
    let comparison = 0;
    
    switch (sortBy) {
      case 'date':
        comparison = new Date(a.booked_at).getTime() - new Date(b.booked_at).getTime();
        break;
      case 'amount':
        comparison = a.amount - b.amount;
        break;
      case 'alert':
        comparison = (a.linked_alert_id || '').localeCompare(b.linked_alert_id || '');
        break;
    }

    return sortDirection === 'asc' ? comparison : -comparison;
  });

  const chipClass = (active: boolean) =>
    cn(
      'inline-flex items-center gap-1 h-8 px-3 rounded-full border text-xs font-medium transition-colors',
      {
        'bg-secondary-container border-secondary-container text-on-secondary-container': active,
        'bg-surface border-outline text-on-surface-variant': !active,
      }
    );

  return (
    <section className="flex flex-col gap-3" aria-labelledby="h-tx">
      <h2 className="text-lg font-semibold text-on-surface" id="h-tx">
        Transaction evidence timeline
      </h2>

      <div className="flex gap-2 overflow-x-auto" role="group" aria-label="Timeline sort and filter">
        <button
          onClick={() => handleSort('date')}
          aria-pressed={sortBy === 'date'}
          className={chipClass(sortBy === 'date')}
        >
          {sortBy === 'date' && (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
            </svg>
          )}
          Date
          {sortBy === 'date' && (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z" />
            </svg>
          )}
        </button>
        <button
          onClick={() => handleSort('amount')}
          aria-pressed={sortBy === 'amount'}
          className={chipClass(sortBy === 'amount')}
        >
          Amount
        </button>
        <button
          onClick={() => handleSort('alert')}
          aria-pressed={sortBy === 'alert'}
          className={chipClass(sortBy === 'alert')}
        >
          Linked alert
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z" />
          </svg>
        </button>
      </div>

      <div className="bg-surface border border-outline-variant rounded-xl p-4">
        {sortedTransactions.map((tx) => (
          <article
            key={tx.transaction_id}
            className="py-3 border-b border-outline-variant last:border-0 min-h-[88px] flex flex-col gap-1"
            aria-label={`Transaction ${tx.transaction_id}, ${formatDateTime(tx.booked_at)}, ${formatCurrency(tx.amount, tx.currency)}, ${tx.counterparty_name || 'counterparty not available'}, corridor ${tx.corridor}, alert ${tx.linked_alert_id}`}
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-semibold text-on-surface">
                {tx.transaction_id} · {formatDateTime(tx.booked_at)}
              </p>
              <p className="text-lg font-semibold text-on-surface">
                {formatCurrency(tx.amount, tx.currency)}
              </p>
            </div>
            <p className="text-sm text-on-surface">
              {tx.counterparty_name ? (
                <>To {tx.counterparty_name}</>
              ) : (
                <span className="text-on-surface-variant">Counterparty not available</span>
              )}
              {' · '}
              {tx.corridor} · outbound
            </p>
            <div className="flex flex-wrap gap-2 mt-1">
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium bg-info-container text-on-info-container">
                Linked alert {tx.linked_alert_id}
              </span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
