import { useNavigate } from 'react-router-dom';
import { cn } from '../../lib/utils';

interface CaseHeaderProps {
  caseNumber: string;
  customerName: string;
  status: string;
}

export function CaseHeader({ caseNumber, customerName, status }: CaseHeaderProps) {
  const navigate = useNavigate();

  const statusBadgeClass = cn(
    'inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium',
    {
      'bg-info-container text-on-info-container': status === 'INVESTIGATING' || status === 'SUBMITTED_FOR_REVIEW',
      'bg-warning-container text-on-warning-container': status === 'PENDING_INFORMATION',
      'bg-success-container text-on-success-container': status === 'REVIEW_READY',
    }
  );

  return (
    <header className="bg-surface border-b border-outline-variant px-4 py-3 flex items-center gap-2">
      <button
        type="button"
        onClick={() => navigate('/alerts')}
        className="w-12 h-12 flex items-center justify-center rounded-full text-primary"
        aria-label="Navigate up to Alerts"
      >
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
        </svg>
      </button>

      <div className="flex-1 min-w-0">
        <h1 className="text-lg font-semibold text-on-surface truncate">
          {caseNumber} · {customerName}
        </h1>
        <p className="text-xs text-on-surface-variant">Case workspace</p>
      </div>

      <span className={statusBadgeClass} role="status">
        {status.replace(/_/g, ' ')}
      </span>

      <button
        type="button"
        className="w-12 h-12 flex items-center justify-center rounded-full text-primary"
        aria-label="More case actions"
      >
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
        </svg>
      </button>
    </header>
  );
}
