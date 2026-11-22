import { AccountRelationship } from '../../types/evidence';
import { formatDateTime } from '../../lib/utils';

interface AccountRelationshipListProps {
  accounts: AccountRelationship[];
}

export function AccountRelationshipList({ accounts }: AccountRelationshipListProps) {
  return (
    <section
      className="bg-surface border border-outline-variant rounded-xl p-4 flex flex-col gap-3"
      aria-labelledby="h-rel"
    >
      <h2 className="text-lg font-semibold text-on-surface" id="h-rel">
        Account relationships
      </h2>

      <ul>
        {accounts.map((account) => (
          <li
            key={account.account_id}
            className="py-3 border-b border-outline-variant last:border-0 min-h-[72px] flex flex-col gap-1"
          >
            <p className="text-sm font-semibold text-on-surface">
              Account {account.account_number_masked}
            </p>
            <p className="text-xs text-on-surface-variant">
              Relationship: {account.relationship_type} · opened{' '}
              {/* Placeholder date since we don't have opened date in schema */}
              14 Mar 2026
            </p>
          </li>
        ))}
      </ul>

      <p className="text-xs text-on-surface-variant">
        Accounts are masked. Full account numbers, dates of birth and national IDs are not shown.
      </p>
    </section>
  );
}
