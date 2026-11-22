// Information Request History List - timeline of requests

import type { InformationRequest } from '../../types/information-request';

interface InformationRequestHistoryListProps {
  requests: InformationRequest[];
}

export function InformationRequestHistoryList({ requests }: InformationRequestHistoryListProps) {
  if (requests.length === 0) {
    return null;
  }

  // Sort chronologically (oldest first for timeline)
  const sortedRequests = [...requests].sort((a, b) => 
    new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  );

  return (
    <section className="bg-[--surface-container-low] border border-[--surface-container-low] rounded-xl p-4 space-y-3">
      <h2 className="text-lg font-semibold">Case state timeline</h2>
      
      <ul className="flex flex-col" aria-label="Case state history">
        {sortedRequests.map(req => (
          <li 
            key={req.information_request_id}
            className="flex gap-3 py-2 border-b border-[--outline-variant]/50 last:border-b-0 min-h-[56px]"
          >
            <span className="w-2 h-2 rounded-full bg-[--primary] mt-1.5 flex-shrink-0"></span>
            <div className="flex-1">
              <p className="text-sm leading-5">
                {req.information_request_id} {req.status === 'RESPONDED' ? 'response received' : 'sent'} 
                {req.status === 'RESPONDED' && req.is_overdue && ' · late'}
                {req.status === 'RESPONDED' && !req.is_overdue && ' · on time'}
              </p>
              <p className="text-xs leading-4 text-[--on-surface-variant] mt-0.5">
                {new Date(req.status === 'RESPONDED' && req.response_received_at ? req.response_received_at : req.created_at)
                  .toLocaleDateString('en-GB', { 
                    day: '2-digit', 
                    month: 'short', 
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    timeZoneName: 'short'
                  })}
              </p>
            </div>
          </li>
        ))}
      </ul>
      
      <p className="text-xs leading-4 text-[--on-surface-variant]">
        Timeliness history (on time / late) is visible to later reviewers as read-only context.
      </p>
    </section>
  );
}
