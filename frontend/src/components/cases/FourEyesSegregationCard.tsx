// Four-Eyes Segregation Card - officer selection with segregation notice

interface Officer {
  user_id: string;
  display_name: string;
  role: string;
}

interface FourEyesSegregationCardProps {
  officers: Officer[];
  selectedOfficerId: string;
  onSelectOfficer: (officerId: string) => void;
}

export function FourEyesSegregationCard({ 
  officers, 
  selectedOfficerId, 
  onSelectOfficer 
}: FourEyesSegregationCardProps) {
  const selectedOfficer = officers.find(o => o.user_id === selectedOfficerId);

  return (
    <section 
      className="bg-[--surface-container-low] border border-[--primary] rounded-xl p-4 space-y-3"
      aria-labelledby="four-eyes-title"
    >
      <div className="flex gap-3 items-start">
        <svg className="w-6 h-6 flex-shrink-0 text-[--primary]" fill="currentColor" viewBox="0 0 24 24">
          <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zM9 8V6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9z"/>
        </svg>
        <div>
          <h2 id="four-eyes-title" className="text-lg font-semibold">Independent review required</h2>
          <p className="text-sm leading-5 mt-1">
            Case creator cannot decide this case. The reviewing officer must be a different person.
          </p>
        </div>
      </div>

      <div className="space-y-1">
        <label htmlFor="officer-select" className="block text-xs leading-4 font-medium text-[--on-surface-variant]">
          Reviewing officer *
        </label>
        <div className="relative">
          <select
            id="officer-select"
            value={selectedOfficerId}
            onChange={e => onSelectOfficer(e.target.value)}
            className="w-full min-h-[56px] border border-[--outline] rounded-xl bg-[--surface] px-4 pr-10 text-base leading-6 appearance-none focus:outline-none focus:border-2 focus:border-[--primary]"
          >
            {officers.map(officer => (
              <option key={officer.user_id} value={officer.user_id}>
                {officer.display_name} ({officer.role})
              </option>
            ))}
          </select>
          <svg 
            className="absolute right-4 top-1/2 -translate-y-1/2 w-6 h-6 text-[--on-surface-variant] pointer-events-none" 
            fill="currentColor" 
            viewBox="0 0 24 24"
          >
            <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"/>
          </svg>
        </div>
        <p className="text-xs leading-3.5 font-semibold text-[--on-surface-variant]">
          Only an officer other than the case creator can be selected. This selection assigns the review; it records no decision.
        </p>
      </div>

      {selectedOfficer && (
        <div className="bg-[--surface] border border-[--outline-variant] rounded-xl p-3">
          <div className="flex items-center gap-2">
            <svg className="w-6 h-6 text-[--on-surface-variant]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
            <div>
              <p className="text-sm font-semibold">{selectedOfficer.display_name}</p>
              <p className="text-xs text-[--on-surface-variant]">{selectedOfficer.role}</p>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
