import { AlertQueueFilters } from '../../types/alert';
import { cn } from '../../lib/utils';

interface AlertFilterBarProps {
  filters: AlertQueueFilters;
  onFiltersChange: (filters: AlertQueueFilters) => void;
}

interface FilterChipProps {
  label: string;
  selected: boolean;
  onClick: () => void;
}

function FilterChip({ label, selected, onClick }: FilterChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-1 h-8 px-3 rounded-full border text-xs font-medium whitespace-nowrap',
        selected
          ? 'bg-secondary-container border-secondary-container text-on-secondary-container'
          : 'bg-surface border-outline text-on-surface-variant'
      )}
      aria-pressed={selected}
    >
      {label}
    </button>
  );
}

export function AlertFilterBar({ filters, onFiltersChange }: AlertFilterBarProps) {
  const updateFilter = (key: keyof AlertQueueFilters, value: string | undefined) => {
    onFiltersChange({
      ...filters,
      [key]: value,
      offset: 0, // Reset to first page when filters change
    });
  };

  const statusOptions = [
    { value: undefined, label: 'Status: All' },
    { value: 'NEW', label: 'Status: New' },
    { value: 'UNDER_REVIEW', label: 'Status: Under Review' },
    { value: 'ESCALATED_TO_CASE', label: 'Status: Escalated' },
    { value: 'CLOSED_NON_ACTIONABLE', label: 'Status: Closed' },
  ];

  const priorityOptions = [
    { value: undefined, label: 'Priority: All' },
    { value: 'CRITICAL', label: 'Priority: Critical' },
    { value: 'HIGH', label: 'Priority: High' },
    { value: 'MEDIUM', label: 'Priority: Medium' },
    { value: 'LOW', label: 'Priority: Low' },
  ];

  const ownerOptions = [
    { value: undefined, label: 'Owner: All' },
    { value: 'UNASSIGNED', label: 'Owner: Unassigned' },
    { value: 'ME', label: 'Owner: Me' },
  ];

  const sortOptions = [
    { value: 'priority', label: 'Sort: Priority' },
    { value: 'risk_score', label: 'Sort: Risk score' },
    { value: 'created_at', label: 'Sort: Date' },
  ];

  return (
    <div className="flex gap-2 overflow-x-auto pb-2" role="group" aria-label="Queue filters">
      {/* Status Filter */}
      <div className="flex gap-2">
        {statusOptions.map((opt) => (
          <FilterChip
            key={opt.label}
            label={opt.label}
            selected={filters.status === opt.value}
            onClick={() => updateFilter('status', opt.value)}
          />
        ))}
      </div>

      {/* Priority Filter */}
      <div className="flex gap-2">
        {priorityOptions.map((opt) => (
          <FilterChip
            key={opt.label}
            label={opt.label}
            selected={filters.priority === opt.value}
            onClick={() => updateFilter('priority', opt.value)}
          />
        ))}
      </div>

      {/* Owner Filter */}
      <div className="flex gap-2">
        {ownerOptions.map((opt) => (
          <FilterChip
            key={opt.label}
            label={opt.label}
            selected={filters.assignee_id === opt.value}
            onClick={() => updateFilter('assignee_id', opt.value)}
          />
        ))}
      </div>

      {/* Sort By */}
      <div className="flex gap-2">
        {sortOptions.map((opt) => (
          <FilterChip
            key={opt.label}
            label={opt.label}
            selected={filters.sort_by === opt.value}
            onClick={() => updateFilter('sort_by', opt.value as 'priority' | 'risk_score' | 'created_at')}
          />
        ))}
      </div>
    </div>
  );
}
