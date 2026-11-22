# Task 5 Handoff: Triage and Investigation Notes

## Implemented Endpoints

### POST /api/v1/alerts/{alert_id}/triage-disposition
Saves triage disposition for an alert with mandatory rationale.

**Request Body:**
```json
{
  "outcome": "INVESTIGATE | CLOSE_NON_ACTIONABLE | MERGE_EXISTING_CASE",
  "rationale": "string (min 10 characters)",
  "existing_case_id": "string | null (required when outcome=MERGE_EXISTING_CASE)"
}
```

**Response 200:**
```json
{
  "alert_id": "string",
  "status": "string",
  "triage_outcome": "string",
  "triage_rationale": "string",
  "triaged_by_user_id": "string",
  "triaged_at": "datetime"
}
```

**Validation:**
- Rationale must be at least 10 characters
- Outcome must be one of: INVESTIGATE, CLOSE_NON_ACTIONABLE, MERGE_EXISTING_CASE
- existing_case_id required when outcome is MERGE_EXISTING_CASE
- Returns 422 for validation failures
- Returns 404 if alert not found

**Status Transitions:**
- INVESTIGATE: keeps current status
- CLOSE_NON_ACTIONABLE: status → CLOSED_NON_ACTIONABLE
- MERGE_EXISTING_CASE: status → MERGED_INTO_EXISTING_CASE

**Audit Trail:**
- Creates ALERT_TRIAGE_RECORDED audit event with outcome, rationale, and status change

---

### GET /api/v1/cases/{case_id}/notes
Retrieves all investigation notes for a case in chronological order.

**Response 200:**
```json
[
  {
    "note_id": "string",
    "case_id": "string",
    "note_type": "string",
    "stage": "string",
    "body": "string",
    "author_user_id": "string",
    "author_display_name": "string",
    "created_at": "datetime",
    "superseded_by_note_id": "string | null"
  }
]
```

**Behavior:**
- Notes returned in chronological order (created_at ASC, oldest to newest)
- Each note includes author information resolved from users table
- superseded_by_note_id tracks note amendments (not editable, new note created)
- Returns 404 if case not found

---

### POST /api/v1/cases/{case_id}/notes
Creates a new investigation note for a case.

**Request Body:**
```json
{
  "note_type": "string",
  "stage": "string",
  "body": "string (min 1 character)"
}
```

**Response 201:**
```json
{
  "note_id": "string",
  "case_id": "string",
  "note_type": "string",
  "stage": "string",
  "body": "string",
  "author_user_id": "string",
  "author_display_name": "string",
  "created_at": "datetime",
  "superseded_by_note_id": null
}
```

**Validation:**
- body cannot be empty (minimum 1 character)
- Returns 422 for validation failures
- Returns 404 if case not found

**Audit Trail:**
- Creates INVESTIGATION_NOTE_ADDED audit event with note metadata

---

## Implementation Details

### New Repository: CaseNoteRepository
Location: `/repos/aml-transaction-monitoring/backend/app/repositories/case_note_repository.py`

**Methods:**
- `create(note: CaseNote) -> CaseNote` - Creates new note
- `list_by_case(case_id: str) -> list[CaseNote]` - Lists notes chronologically
- `get_user_by_id(user_id: str) -> User | None` - Enriches with author info

### Updated AlertRepository
**New Method:**
- `save_triage_disposition(alert, outcome, rationale, actor_id)` - Saves triage and updates status

### Updated AlertService
**New Method:**
- `save_triage_disposition(alert_id, outcome, rationale, actor_id, existing_case_id)` - Business logic and validation

### Updated CaseService
**New Methods:**
- `create_note(case_id, note_type, stage, body, author_user_id) -> CaseNoteResponse` - Creates note with audit
- `list_notes(case_id) -> list[CaseNoteResponse]` - Lists notes with enrichment

### Updated Seed Data
The seed now includes:
- Sample triage outcomes on alerts (alert-006: INVESTIGATE, alert-007: CLOSE_NON_ACTIONABLE)
- 5 investigation notes across 2 cases (CS-001: 3 notes, CS-002: 2 notes)
- Note types: INVESTIGATION, ANALYSIS
- Stages: INITIAL_REVIEW, DETAILED_ANALYSIS, ONGOING_MONITORING
- Audit events for note creation

---

## Test Coverage

### Unit Tests (test_triage_service.py)
- ✓ save_triage_disposition with CLOSE_NON_ACTIONABLE
- ✓ INVESTIGATE keeps current status
- ✓ MERGE_EXISTING_CASE transitions to MERGED_INTO_EXISTING_CASE
- ✓ Validates rationale minimum 10 characters
- ✓ Validates outcome is valid
- ✓ Validates existing_case_id required for MERGE_EXISTING_CASE
- ✓ Alert not found raises ValueError
- ✓ Creates audit event

### Integration Tests (test_triage_integration.py)
- ✓ POST triage disposition with CLOSE_NON_ACTIONABLE
- ✓ POST triage disposition with INVESTIGATE
- ✓ POST triage disposition with MERGE_EXISTING_CASE
- ✓ Validates rationale length (returns 422)
- ✓ Alert not found (returns 404)
- ✓ GET case notes returns chronological order
- ✓ GET case notes includes author info
- ✓ POST case note creates note (returns 201)
- ✓ POST case note validates empty body (returns 422)
- ✓ POST case note case not found (returns 404)

---

## API Contract Summary

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/alerts/{alert_id}/triage-disposition` | POST | Required | Save triage disposition with rationale (min 10 chars) |
| `/api/v1/cases/{case_id}/notes` | GET | Required | List notes chronologically |
| `/api/v1/cases/{case_id}/notes` | POST | Required | Create investigation note |

**Triage Outcomes:**
- INVESTIGATE - Requires further investigation (keeps current status)
- CLOSE_NON_ACTIONABLE - Verified legitimate (status → CLOSED_NON_ACTIONABLE)
- MERGE_EXISTING_CASE - Link to existing case (status → MERGED_INTO_EXISTING_CASE, requires existing_case_id)

**Note Chronology:**
- Notes displayed oldest to newest (created_at ASC)
- Each note shows author, timestamp, type, stage
- Notes are immutable (amendments create new note with superseded_by_note_id reference)

---

## Seed Data Access

**Login Credentials:**
- Username: `riya` / Password: `password123` (Investigator)
- Username: `morgan` / Password: `password123` (Officer)

**Sample Cases with Notes:**
- CS-001: 3 notes (initial review, analysis, monitoring)
- CS-002: 2 notes (initial review, analysis)

**Sample Alerts with Triage:**
- alert-006: INVESTIGATE outcome, triaged by riya
- alert-007: CLOSE_NON_ACTIONABLE outcome, triaged by riya
