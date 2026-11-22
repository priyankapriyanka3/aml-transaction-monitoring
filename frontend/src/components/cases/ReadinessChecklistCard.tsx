// Readiness Checklist Card - shows 4-item checklist for handoff readiness

import type { ReadinessCheck } from '../../types/handoff';

interface ReadinessChecklistCardProps {
  readiness: ReadinessCheck;
}

export function ReadinessChecklistCard({ readiness }: ReadinessChecklistCardProps) {
  const completedCount = readiness.checklist_items.filter(item => item.passed).length;
  const totalCount = readiness.checklist_items.length;

  return (
    <section 
      className="bg-[--surface] border border-[--outline-variant] rounded-xl p-4 space-y-3"
      aria-labelledby="checklist-title"
      aria-live="polite"
    >
      <div className="flex justify-between items-center gap-2">
        <h2 id="checklist-title" className="text-lg font-semibold">Readiness checklist</h2>
        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs leading-4 font-medium ${
          readiness.is_ready 
            ? 'bg-[--success-container] text-[--on-success-container]' 
            : 'bg-[--warning-container] text-[--on-warning-container]'
        }`}>
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            {readiness.is_ready ? (
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            ) : (
              <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
            )}
          </svg>
          {completedCount} of {totalCount} complete
        </span>
      </div>

      <ul>
        {readiness.checklist_items.map(item => (
          <li 
            key={item.code}
            className="flex gap-3 items-start min-h-[56px] py-2 border-b border-[--outline-variant]/50 last:border-b-0"
          >
            <svg 
              className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                item.passed ? 'text-[--success]' : 'text-[--warning]'
              }`} 
              fill="currentColor" 
              viewBox="0 0 24 24"
            >
              {item.passed ? (
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              ) : (
                <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
              )}
            </svg>
            <div className="flex-1">
              <p className="text-sm font-semibold leading-5">
                {item.label} 
                <span className={`font-normal ml-1 ${
                  item.passed ? 'text-[--on-surface-variant]' : 'text-[--warning]'
                }`}>
                  · {item.passed ? 'complete' : 'incomplete'}
                </span>
              </p>
              <p className="text-xs leading-4 text-[--on-surface-variant] mt-0.5">
                {item.detail}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
