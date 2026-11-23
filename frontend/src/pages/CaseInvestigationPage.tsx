import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import type { CaseWorkspaceResponse, CaseNote } from '../types/api';
import '../styles/design-system.css';
import '../styles/components.css';

type NoteCategory = 'investigation' | 'recommendation' | 'information_request' | 'response' | 'closure';

type TabType = 'overview' | 'linked-alerts' | 'requests' | 'audit';

export default function CaseInvestigationPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [workspace, setWorkspace] = useState<CaseWorkspaceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [selectedCategory, setSelectedCategory] = useState<NoteCategory>('investigation');
  const [noteText, setNoteText] = useState('');
  const [saving, setSaving] = useState(false);
  const [snackbar, setSnackbar] = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) return;
    loadWorkspace();
  }, [caseId]);

  const loadWorkspace = async () => {
    if (!caseId) return;
    try {
      setLoading(true);
      const data = await apiClient.getCaseWorkspace(caseId);
      setWorkspace(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load case workspace');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNote = async () => {
    if (!caseId || !noteText.trim()) return;
    try {
      setSaving(true);
      await apiClient.addCaseNote(caseId, {
        note_category: selectedCategory,
        note_text: noteText.trim(),
      });
      setNoteText('');
      await loadWorkspace();
      setSnackbar('Note saved successfully');
      setTimeout(() => setSnackbar(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save note');
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return `${formatDate(dateString)}, ${date.toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    })} UTC`;
  };

  const getStatusBadgeClass = (status: string) => {
    const statusMap: Record<string, string> = {
      OPEN: 'b-info',
      INVESTIGATING: 'b-info',
      PENDING_INFORMATION: 'b-warn',
      UNDER_REVIEW: 'b-pri',
      APPROVED: 'b-ok',
      REJECTED: 'b-crit',
    };
    return `badge ${statusMap[status] || 'b-neu'}`;
  };

  const getCategoryBadgeClass = (category: string) => {
    const categoryMap: Record<string, string> = {
      investigation: 'b-info',
      recommendation: 'b-neu',
      information_request: 'b-warn',
      response: 'b-ok',
      closure: 'b-pri',
    };
    return `badge ${categoryMap[category] || 'b-neu'}`;
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      investigation: 'Investigation',
      recommendation: 'Recommendation',
      information_request: 'Information request',
      response: 'Response',
      closure: 'Closure',
    };
    return labels[category] || category;
  };

  if (loading) {
    return (
      <div className="page">
        <div className="loading-state">Loading case workspace...</div>
      </div>
    );
  }

  if (error || !workspace) {
    return (
      <div className="page">
        <div className="error-state">
          <p>{error || 'Case not found'}</p>
          <button onClick={() => navigate('/alerts')} className="btn btn-o">
            Back to alerts
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-header">
        <button onClick={() => navigate('/alerts')} className="icon-btn" aria-label="Back to alerts">
          ←
        </button>
        <div className="page-header-content">
          <p className="eyebrow">TRANSFER REVIEW · CASE WORKSPACE</p>
          <h1 className="page-title">{workspace.case_ref}</h1>
        </div>
      </header>

      <div className="tabs-row">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'linked-alerts' ? 'active' : ''}`}
          onClick={() => setActiveTab('linked-alerts')}
        >
          Linked alerts ({workspace.linked_alerts.total})
        </button>
        <button
          className={`tab ${activeTab === 'requests' ? 'active' : ''}`}
          onClick={() => setActiveTab('requests')}
        >
          Requests (0)
        </button>
        <button
          className={`tab ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          Audit
        </button>
      </div>

      {activeTab === 'overview' && (
        <main className="page-content">
          <div className="row space-between">
            <span className={getStatusBadgeClass(workspace.status)}>
              {workspace.status.replace(/_/g, ' ').toLowerCase()}
            </span>
            <p className="text-sm text-muted">
              Opened {formatDate(workspace.created_at_utc)}
            </p>
          </div>

          {workspace.current_blocker_state !== 'NONE' && (
            <div className="banner banner-warn" role="status" aria-live="polite">
              <span className="banner-icon">⚠️</span>
              <div className="banner-content">
                <p className="banner-title">
                  {workspace.current_blocker_state === 'OPEN_REQUESTS' ? 'Open requests — decision blocked' : 'Overdue requests — decision blocked'}
                </p>
                <p className="banner-text">
                  Approval, rejection and closure remain blocked while any request is open or overdue.
                </p>
              </div>
            </div>
          )}

          <section className="section">
            <h2 className="section-title">Linked alerts</h2>
            {workspace.linked_alerts.items.map((alert) => (
              <div
                key={alert.alert_id}
                className={`card ${alert.is_primary ? 'card-primary' : ''}`}
              >
                <div className="row space-between">
                  <h3 className="card-title">{alert.alert_ref}</h3>
                  <span className={`badge ${alert.is_primary ? 'b-pri' : 'b-neu'}`}>
                    {alert.is_primary ? 'Primary · opened case' : 'Linked'}
                  </span>
                </div>
                <p className="text-sm text-muted">
                  Linked {formatDateTime(alert.linked_at_utc)}
                </p>
              </div>
            ))}
          </section>

          <section className="card">
            <h2 className="section-title">Investigation narrative</h2>
            
            <div className="filter-chips">
              {(['investigation', 'recommendation', 'information_request', 'response', 'closure'] as NoteCategory[]).map((cat) => (
                <button
                  key={cat}
                  className={`chip ${selectedCategory === cat ? 'chip-selected' : ''}`}
                  onClick={() => setSelectedCategory(cat)}
                >
                  {selectedCategory === cat && '✓ '}
                  {getCategoryLabel(cat)}
                </button>
              ))}
            </div>

            <div className="form-field form-field-multi">
              <label className="form-label">Note *</label>
              <textarea
                className="form-input"
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                placeholder="Enter investigation note..."
                rows={4}
              />
            </div>
            <p className="text-sm text-muted">{noteText.length} / 2000</p>

            <button
              onClick={handleSaveNote}
              disabled={!noteText.trim() || saving}
              className="btn btn-primary btn-block"
            >
              {saving ? 'Saving...' : 'Save note'}
            </button>

            {workspace.notes.items.length > 0 && (
              <div className="notes-history">
                {workspace.notes.items.map((note: CaseNote) => (
                  <div key={note.note_id} className="note-item">
                    <div className="row space-between">
                      <span className={getCategoryBadgeClass(note.note_category)}>
                        {getCategoryLabel(note.note_category)}
                      </span>
                      <span className="text-sm text-muted">
                        {formatDateTime(note.authored_at_utc)}
                      </span>
                    </div>
                    <p className="note-text">{note.note_text}</p>
                  </div>
                ))}
              </div>
            )}
            <p className="text-sm text-muted">Notes are append-only. Earlier entries cannot be edited or removed.</p>
          </section>

          <section className="card">
            <h2 className="section-title">Activity timeline</h2>
            <div className="timeline">
              {workspace.timeline_entries.items.map((entry) => (
                <div key={entry.event_id} className="timeline-item">
                  <div className="timeline-dot"></div>
                  <div className="timeline-content">
                    <p className="timeline-title">{entry.action_type.replace(/_/g, ' ').toLowerCase()}</p>
                    <p className="text-sm text-muted">
                      {formatDateTime(entry.occurred_at_utc)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </main>
      )}

      {snackbar && (
        <div className="snackbar" role="status" aria-live="polite">
          {snackbar}
        </div>
      )}
    </div>
  );
}
