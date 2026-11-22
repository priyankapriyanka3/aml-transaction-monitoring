// Decision Blocker Banner - shows when requests block decision actions

interface DecisionBlockerBannerProps {
  openCount: number;
  overdueCount: number;
}

export function DecisionBlockerBanner({ openCount, overdueCount }: DecisionBlockerBannerProps) {
  const totalBlockers = openCount + overdueCount;
  
  if (totalBlockers === 0) {
    return (
      <div 
        className="bg-[--success-container] text-[--on-surface] rounded-2xl p-4 flex gap-3 items-start"
        role="status"
        aria-live="polite"
      >
        <svg className="w-6 h-6 flex-shrink-0 text-[--success]" fill="currentColor" viewBox="0 0 24 24">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
        <div>
          <p className="font-medium text-sm leading-5">No open requests</p>
          <p className="text-xs leading-4 mt-1 text-[--on-surface-variant]">All requests on this case are fulfilled or closed.</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="bg-[--warning-container] text-[--on-surface] rounded-2xl p-4 flex gap-3 items-start"
      role="status"
      aria-live="polite"
    >
      <svg className="w-6 h-6 flex-shrink-0 text-[--warning]" fill="currentColor" viewBox="0 0 24 24">
        <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
      </svg>
      <div>
        <p className="font-medium text-sm leading-5">
          {totalBlockers} open request{totalBlockers !== 1 ? 's' : ''} — decision blocked
        </p>
        <p className="text-xs leading-4 mt-1 text-[--on-surface-variant]">
          Approval, rejection and closure remain blocked while any request is open or overdue.
        </p>
      </div>
    </div>
  );
}
