import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../lib/api-client';
import { useAuth } from '../lib/auth-context';
import { Alert, AlertQueueFilters, AlertQueueResponse, TriageDispositionRequest } from '../types/alert';
import { HeroAlertCard } from '../components/alerts/HeroAlertCard';
import { AlertFilterBar } from '../components/alerts/AlertFilterBar';
import { TriageDispositionModal } from '../components/alerts/TriageDispositionModal';
import { formatCurrency, formatDateTime, cn } from '../lib/utils';

export function AlertQueuePage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [assigningAlert, setAssigningAlert] = useState<string | null>(null);
  const [triageAlertId, setTriageAlertId] = useState<string | null>(null);

  const [filters, setFilters] = useState<AlertQueueFilters>({
    sort_by: 'risk_score',
    sort_direction: 'desc',
    limit: 20,
    offset: 0,
  });

  useEffect(() => {
    loadAlerts();
  }, [filters]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError('');

      // Build query params
      const params = new URLSearchParams();
      if (filters.status) params.set('status', filters.status);
      if (filters.priority) params.set('priority', filters.priority);
      if (filters.assignee_id) {
        if (filters.assignee_id === 'ME' && user) {
          params.set('assignee_id', user.user_id);
        } else if (filters.assignee_id === 'UNASSIGNED') {
          params.set('assignee_id', 'UNASSIGNED');
        } else {
          params.set('assignee_id', filters.assignee_id);
        }
      }
      if (filters.risk_score_min !== undefined) params.set('risk_score_min', filters.risk_score_min.toString());
      if (filters.risk_score_max !== undefined) params.set('risk_score_max', filters.risk_score_max.toString());
      if (filters.generation) params.set('generation', filters.generation);
      if (filters.search) params.set('search', filters.search);
      if (filters.sort_by) params.set('sort_by', filters.sort_by);
      if (filters.sort_direction) params.set('sort_direction', filters.sort_direction);
      params.set('limit', (filters.limit ?? 20).toString());
      params.set('offset', (filters.offset ?? 0).toString());

      const response = await apiClient.get<AlertQueueResponse>(`/alerts?${params.toString()}`);
      setAlerts(response.items);
      setTotalCount(response.total_count);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const handleAssign = async (alertId: string) => {
    if (!user) return;

    try {
      setAssigningAlert(alertId);
      await apiClient.post(`/alerts/${alertId}/claim`, {
        assignee_user_id: user.user_id,
        assignment_reason: 'Self-assigned for investigation',
      });
      // Reload alerts after assignment
      await loadAlerts();
    } catch (err) {
      console.error('Failed to assign alert:', err);
    } finally {
      setAssigningAlert(null);
    }
  };

  const handleTriageSubmit = async (request: TriageDispositionRequest) => {
    if (!triageAlertId) return;

    try {
      await apiClient.post(`/alerts/${triageAlertId}/triage-disposition`, request);
      // Reload alerts after triage
      await loadAlerts();
      setTriageAlertId(null);
    } catch (err) {
      console.error('Failed to save triage disposition:', err);
      throw err;
    }
  };

  const handleCreateCase = async (alertId: string) => {
    try {
      // Find the alert to get its priority and triage rationale
      const alert = alerts.find(a => a.alert_id === alertId);
      const response = await apiClient.post<{ case_id: string; case_number: string }>(
        `/alerts/${alertId}/cases`,
        {
          case_priority: alert?.priority || 'MEDIUM',
          initial_rationale: alert?.triage_rationale || 'Case created from alert requiring investigation'
        }
      );
      // Navigate to the new case
      navigate(`/cases/${response.case_number}`);
    } catch (err) {
      console.error('Failed to create case:', err);
    }
  };

  // Hero alert (highest priority, first in queue)
  const heroAlert = alerts[0];
  const secondaryAlerts = alerts.slice(1);

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Top App Bar */}
      <header className="bg-surface border-b border-outline-variant px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-on-surface">Alerts</h1>
            <p className="text-sm text-on-surface-variant">
              {totalCount} alert{totalCount !== 1 ? 's' : ''} in queue
            </p>
          </div>
          {user && (
            <div className="flex items-center gap-2 px-3 py-2 bg-info-container rounded-lg">
              <svg className="w-5 h-5 text-info" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
              </svg>
              <span className="text-xs font-medium text-on-info-container">{user.primary_role}</span>
            </div>
          )}
        </div>
      </header>

      {/* Alert Filter Bar */}
      <AlertFilterBar filters={filters} onFiltersChange={setFilters} />

      {/* Main Content */}
      <main className="px-4 py-6 flex flex-col gap-6">
        {/* Error State */}
        {error && (
          <div
            className="bg-critical-container text-on-critical-container rounded-xl p-4 flex gap-3"
            role="alert"
          >
            <svg className="w-6 h-6 flex-none" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
            </svg>
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div
            className="flex items-center justify-center p-8"
            role="status"
            aria-label="Loading alert queue"
          >
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Hero Alert */}
        {!loading && heroAlert && (
          <section aria-labelledby="h-hero">
            <h2 className="text-sm font-medium text-on-surface mb-3" id="h-hero">
              Highest priority
            </h2>
            <HeroAlertCard
              alert={heroAlert}
              onAssign={handleAssign}
              onCreateCase={handleCreateCase}
              isAssigning={assigningAlert === heroAlert.alert_id}
              currentUserId={user?.user_id}
            />
          </section>
        )}

        {/* Secondary Alerts */}
        {!loading && secondaryAlerts.length > 0 && (
          <section aria-labelledby="h-queue">
            <h2 className="text-sm font-medium text-on-surface mb-3" id="h-queue">
              Queue ({secondaryAlerts.length} more)
            </h2>
            {secondaryAlerts.map((alert) => (
              <article
                key={alert.alert_id}
                className="bg-surface border border-outline-variant rounded-xl p-4 mb-3 flex flex-col gap-3"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={cn('inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium', {
                          'bg-critical-container text-on-critical-container': alert.priority === 'CRITICAL',
                          'bg-warning-container text-on-warning-container': alert.priority === 'HIGH',
                          'bg-info-container text-on-info-container': alert.priority === 'MEDIUM',
                        })}
                      >
                        {alert.priority}
                      </span>
                      <span className="text-xs text-on-surface-variant">Risk {alert.risk_score}/100</span>
                    </div>
                    <p className="text-base font-semibold text-on-surface mb-1">
                      {formatCurrency(alert.transaction_amount || 0, alert.transaction_currency || 'USD')}
                    </p>
                    <p className="text-sm text-on-surface truncate">{alert.customer_name || 'Unknown customer'}</p>
                  </div>
                  <div className="flex flex-col gap-2 flex-none">
                    {!alert.assigned_user_id ? (
                      <button
                        type="button"
                        onClick={() => handleAssign(alert.alert_id)}
                        disabled={assigningAlert === alert.alert_id}
                        className="min-h-[40px] px-4 rounded-lg bg-primary text-on-primary text-sm font-semibold disabled:opacity-50"
                      >
                        {assigningAlert === alert.alert_id ? 'Assigning...' : 'Assign to me'}
                      </button>
                    ) : (
                      <span className="text-xs text-on-surface-variant px-4 py-2">
                        Assigned: {alert.assigned_user_name}
                      </span>
                    )}
                    {alert.assigned_user_id && !alert.triage_outcome && (
                      <button
                        type="button"
                        onClick={() => setTriageAlertId(alert.alert_id)}
                        className="min-h-[40px] px-4 rounded-lg border border-outline bg-surface text-primary text-sm font-semibold"
                      >
                        Triage
                      </button>
                    )}
                    {alert.triage_outcome === 'INVESTIGATE' && (
                      <button
                        type="button"
                        onClick={() => handleCreateCase(alert.alert_id)}
                        className="min-h-[40px] px-4 rounded-lg bg-primary text-on-primary text-sm font-semibold"
                      >
                        Create case
                      </button>
                    )}
                  </div>
                </div>
              </article>
            ))}
          </section>
        )}

        {/* Empty State */}
        {!loading && alerts.length === 0 && (
          <div className="bg-surface border border-outline-variant rounded-xl p-8 flex flex-col items-center gap-4 text-center">
            <svg className="w-12 h-12 text-on-surface-variant" fill="currentColor" viewBox="0 0 24 24">
              <path d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z" />
            </svg>
            <h3 className="text-lg font-semibold text-on-surface">No alerts match these filters</h3>
            <p className="text-sm text-on-surface-variant">
              Try widening Status, Priority or Owner, or search a different customer or transaction ID.
            </p>
            <button
              type="button"
              onClick={() => setFilters({ sort_by: 'risk_score', sort_direction: 'desc', limit: 20, offset: 0 })}
              className="min-h-[48px] px-6 rounded-xl bg-primary text-on-primary text-sm font-semibold"
            >
              Clear filters
            </button>
          </div>
        )}

        {/* Audit Guidance */}
        <aside
          className="bg-surface-container-low border border-surface-container-low rounded-xl p-4 flex gap-3"
          role="note"
        >
          <svg className="w-6 h-6 flex-none text-info" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" />
          </svg>
          <p className="text-xs text-on-surface">
            Every assignment and disposition is recorded with your user ID, role and UTC time.
          </p>
        </aside>
      </main>

      {/* Bottom Navigation */}
      <nav
        className="fixed bottom-0 left-0 right-0 bg-surface-container h-20 border-t border-outline-variant flex"
        aria-label="Primary"
      >
        <Link
          to="/alerts"
          className="flex-1 flex flex-col items-center justify-center gap-1 text-primary font-semibold"
          aria-current="page"
        >
          <span className="w-16 h-8 rounded-2xl bg-secondary-container flex items-center justify-center">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z" />
            </svg>
          </span>
          <span className="text-xs">Alerts</span>
        </Link>
        <Link
          to="/cases"
          className="flex-1 flex flex-col items-center justify-center gap-1 text-on-surface-variant"
        >
          <span className="w-16 h-8 rounded-2xl flex items-center justify-center">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
            </svg>
          </span>
          <span className="text-xs">Cases</span>
        </Link>
      </nav>

      {/* Triage Modal */}
      <TriageDispositionModal
        alertId={triageAlertId || ''}
        isOpen={!!triageAlertId}
        onClose={() => setTriageAlertId(null)}
        onSubmit={handleTriageSubmit}
      />
    </div>
  );
}
