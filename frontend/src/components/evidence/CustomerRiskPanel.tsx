import { CustomerContext } from '../../types/evidence';
import { formatDateTime, cn } from '../../lib/utils';

interface CustomerRiskPanelProps {
  customer: CustomerContext;
}

export function CustomerRiskPanel({ customer }: CustomerRiskPanelProps) {
  // Parse exposure indicators
  let exposureIndicators: string[] = [];
  try {
    exposureIndicators = JSON.parse(customer.exposure_indicators_json || '[]');
  } catch {
    exposureIndicators = [];
  }

  // Calculate volume multiplier (hardcoded for demo)
  const expectedVolume = 18000;
  const observedVolume = 96400;
  const volumeMultiplier = observedVolume / expectedVolume;

  const riskRating = customer.risk_rating || 'UNKNOWN';
  const kycReviewDate = customer.kyc_review_date || new Date().toISOString();

  const riskBadgeClass = cn(
    'inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium',
    {
      'bg-critical-container text-on-critical-container': riskRating === 'HIGH',
      'bg-warning-container text-on-warning-container': riskRating === 'MEDIUM',
      'bg-success-container text-on-success-container': riskRating === 'LOW',
    }
  );

  const countryRiskBadgeClass = 'inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium bg-warning-container text-on-warning-container';
  const infoBadgeClass = 'inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium bg-info-container text-on-info-container';

  return (
    <section
      className="bg-surface-container-low border border-surface-container-low rounded-xl p-4 flex flex-col gap-3"
      aria-labelledby="h-cust"
    >
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-on-surface" id="h-cust">
          Customer risk context
        </h2>
        <span className={riskBadgeClass}>
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
          {riskRating} risk
        </span>
      </div>

      <p className="text-sm font-semibold text-on-surface">
        {customer.customer_name} · {customer.customer_id}
      </p>

      <dl className="grid grid-cols-2 gap-x-4 gap-y-3">
        <div>
          <dt className="text-xs font-medium text-on-surface-variant">Customer risk rating</dt>
          <dd className="text-sm text-on-surface">
            {riskRating} · as of {formatDateTime(kycReviewDate).split(',')[0]}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-on-surface-variant">Country risk</dt>
          <dd>
            <span className={countryRiskBadgeClass}>
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
              </svg>
              Elevated · AE
            </span>
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-on-surface-variant">Onboarded</dt>
          <dd className="text-sm text-on-surface">
            {formatDateTime(kycReviewDate).split(',')[0]}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-on-surface-variant">Business type</dt>
          <dd className="text-sm text-on-surface">
            {customer.onboarding_profile === 'corporate' ? 'Import / export trading' : customer.onboarding_profile}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-on-surface-variant">Expected monthly volume</dt>
          <dd className="text-sm text-on-surface">USD {expectedVolume.toLocaleString()}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-on-surface-variant">Observed monthly volume</dt>
          <dd className="text-sm font-semibold text-on-surface">USD {observedVolume.toLocaleString()}</dd>
        </div>
      </dl>

      <div>
        <div
          className="h-2 rounded bg-surface-variant overflow-hidden"
          role="img"
          aria-label={`Observed volume is ${volumeMultiplier.toFixed(1)} times the expected volume`}
        >
          <div className="h-2 bg-primary" style={{ width: '100%' }} />
        </div>
        <p className="text-xs text-on-surface-variant mt-1">
          Observed is {volumeMultiplier.toFixed(1)}× expected volume.
        </p>
      </div>

      <span className={infoBadgeClass}>
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" />
        </svg>
        Risk values as of {formatDateTime(kycReviewDate).split(',')[0]}
      </span>
    </section>
  );
}
