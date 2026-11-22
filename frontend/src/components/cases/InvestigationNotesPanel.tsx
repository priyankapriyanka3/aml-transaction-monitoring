import { useState } from 'react';
import { CaseNote, CaseNoteRequest } from '../../types/case';
import { formatDateTime } from '../../lib/utils';

interface InvestigationNotesPanelProps {
  caseId: string;
  notes: CaseNote[];
  onSaveNote: (request: CaseNoteRequest) => Promise<void>;
}

export function InvestigationNotesPanel({ caseId, notes, onSaveNote }: InvestigationNotesPanelProps) {
  const [noteBody, setNoteBody] = useState('');
  const [stage, setStage] = useState('INVESTIGATION');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    if (!noteBody.trim()) {
      setError('Note body cannot be empty');
      return;
    }

    try {
      setIsSaving(true);
      setError('');

      await onSaveNote({
        note_type: 'INVESTIGATION',
        stage,
        body: noteBody.trim(),
      });

      // Clear form on success
      setNoteBody('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save note');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <section className="flex flex-col gap-3" aria-labelledby="h-notes">
      <h2 className="text-sm font-medium text-on-surface" id="h-notes">
        Investigation notes
      </h2>

      {/* Stage Selector */}
      <div className="flex border border-outline rounded-full overflow-hidden" role="group" aria-label="Note stage">
        {['Triage', 'Investigation', 'Info request', 'Findings'].map((stageName, index) => {
          const stageValue = ['TRIAGE', 'INVESTIGATION', 'INFO_REQUEST', 'FINDINGS'][index];
          return (
            <button
              key={stageValue}
              type="button"
              onClick={() => setStage(stageValue)}
              className={`flex-1 min-h-[40px] text-xs font-medium ${
                stage === stageValue
                  ? 'bg-secondary-container text-on-secondary-container'
                  : 'bg-surface text-on-surface'
              }`}
              aria-pressed={stage === stageValue}
            >
              {stageName}
            </button>
          );
        })}
      </div>

      {/* Note Composition */}
      <div className="flex flex-col gap-1">
        <label htmlFor="note-input" className="text-xs font-medium text-on-surface-variant">
          Note · {stage.replace(/_/g, ' ')}
        </label>
        <textarea
          id="note-input"
          value={noteBody}
          onChange={(e) => setNoteBody(e.target.value)}
          className={`w-full min-h-[112px] px-4 py-3 border rounded-xl bg-surface text-on-surface text-base resize-none ${
            error ? 'border-critical' : 'border-outline focus:border-primary'
          }`}
          placeholder="Add investigation note..."
        />
        <div className="flex items-center justify-between">
          <p className="text-xs text-on-surface-variant">Edits create a new visible version.</p>
          <p className="text-xs text-on-surface-variant">{noteBody.length} / 2000</p>
        </div>
      </div>

      {error && (
        <p className="text-xs text-critical" role="alert">
          {error}
        </p>
      )}

      <button
        type="button"
        onClick={handleSave}
        disabled={isSaving || !noteBody.trim()}
        className="min-h-[48px] px-4 border border-outline rounded-xl bg-surface text-primary text-sm font-semibold disabled:opacity-38"
      >
        {isSaving ? 'Saving...' : 'Save note'}
      </button>

      {/* Notes List */}
      {notes.length > 0 && (
        <ul className="flex flex-col gap-3" aria-label="Notes, oldest first">
          {notes.map((note) => (
            <li key={note.note_id} className="border-l-4 border-secondary-container pl-3 flex flex-col gap-1">
              <p className="text-xs uppercase font-semibold text-on-surface-variant tracking-wide">
                {note.stage.replace(/_/g, ' ')} · {note.author_display_name} · {formatDateTime(note.created_at)}
                {note.superseded_by_note_id && (
                  <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-lg bg-surface-variant text-on-surface-variant normal-case">
                    Edited
                  </span>
                )}
              </p>
              <p className="text-sm text-on-surface">{note.body}</p>
            </li>
          ))}
        </ul>
      )}

      {notes.length === 0 && (
        <div className="bg-surface border border-outline-variant rounded-xl p-8 flex flex-col items-center gap-4 text-center">
          <svg className="w-12 h-12 text-on-surface-variant" fill="currentColor" viewBox="0 0 24 24">
            <path d="M3 18h12v-2H3v2zM3 6v2h18V6H3zm0 7h18v-2H3v2z" />
          </svg>
          <h3 className="text-lg font-semibold text-on-surface">No notes yet</h3>
          <p className="text-sm text-on-surface-variant">Add the first investigation note for this stage.</p>
        </div>
      )}
    </section>
  );
}
