# TASK-6 Handoff: Investigation Notes and Case Workspace

## Implemented Endpoints

### POST /api/v1/cases/{caseId}/notes
Captures attributable investigation notes with author identity and timestamp.

**Request:**
```json
{
  "note_category": "investigation|recommendation|information_request|response|closure",
  "note_text": "Investigation narrative content"
}
```

**Response (201 Created):**
```json
{
  "note_id": "uuid",
  "case_id": "uuid",
  "note_category": "investigation",
  "note_text": "Investigation narrative content",
  "author_user_id": "uuid",
  "authored_at_utc": "2026-11-22T14:30:00Z"
}
```

**Behavior:**
- Captures author identity from authenticated user context (JWT token)
- Records timestamp automatically at creation
- Creates NOTE_ADDED audit event with correlation_id
- Returns 404 if case not found
- Requires X-Correlation-ID header for audit trail

---

### GET /api/v1/cases/{caseId}/workspace
Returns complete case workspace with progress restoration capability.

**Response (200 OK):**
```json
{
  "case_id": "uuid",
  "case_ref": "CS-204",
  "status": "INVESTIGATING",
  "current_blocker_state": "NONE",
  "created_by_user_id": "uuid",
  "assigned_officer_user_id": "uuid|null",
  "created_at_utc": "2026-11-22T10:00:00Z",
  "updated_at_utc": "2026-11-22T14:00:00Z",
  "linked_alerts": {
    "items": [
      {
        "alert_id": "uuid",
        "alert_ref": "ALT-2026-001",
        "is_primary": true,
        "linked_at_utc": "2026-11-22T10:00:00Z"
      }
    ],
    "total": 1
  },
  "notes": {
    "items": [
      {
        "note_id": "uuid",
        "note_category": "investigation",
        "note_text": "Investigation narrative...",
        "author_user_id": "uuid",
        "authored_at_utc": "2026-11-22T14:30:00Z"
      }
    ],
    "total": 1
  },
  "evidence_gaps": {
    "items": [],
    "total": 0
  },
  "timeline_entries": {
    "items": [
      {
        "event_id": "uuid",
        "action_type": "CASE_CREATED",
        "actor_user_id": "uuid",
        "occurred_at_utc": "2026-11-22T10:00:00Z",
        "details_json": "{...}"
      }
    ],
    "total": 1
  }
}
```

**Behavior:**
- Aggregates case metadata, linked alerts, notes, evidence gaps (empty for now), and timeline
- All arrays use `{items: [...], total: N}` structure for frontend pagination support
- Linked alerts ordered by linked_at_utc ASC (primary alert first)
- Notes ordered by authored_at_utc DESC (most recent first)
- Timeline entries ordered by occurred_at_utc DESC (most recent first)
- Returns 404 if case not found
- Supports progress restoration after information request resolution by maintaining complete case context

---

## Database Schema

### case_notes Table
```sql
CREATE TABLE case_notes (
  note_id UUID PRIMARY KEY,
  case_id UUID NOT NULL REFERENCES aml_cases(case_id),
  note_category VARCHAR(32) NOT NULL,
  note_text TEXT NOT NULL,
  author_user_id UUID NOT NULL REFERENCES users(user_id),
  authored_at_utc TIMESTAMP NOT NULL
);

CREATE INDEX ix_case_notes_case_id ON case_notes(case_id);
```

**Note Categories:**
- investigation
- recommendation
- information_request
- response
- closure

---

## Seed Data

### Sample Cases with Notes (CS-201, CS-202, CS-203)

**CS-201 (OPEN status):**
- Primary alert: ALT-2026-001 (40000000-0000-0000-0000-000000000001)
- 3 notes:
  - Note 80000000-0000-0000-0000-000000000001 (investigation): "Initial review of alert ALT-2026-001: High-value transaction ($95,000 USD) from GB to VG..."
  - Note 80000000-0000-0000-0000-000000000002 (information_request): "Requested additional documentation from customer..."
  - Note 80000000-0000-0000-0000-000000000003 (investigation): "Customer provided invoice dated 2026-11-20..."

**CS-202 (INVESTIGATING status):**
- Primary alert: ALT-2026-002 (40000000-0000-0000-0000-000000000002)
- 3 notes:
  - Note 80000000-0000-0000-0000-000000000004 (investigation): "Alert ALT-2026-002 triggered on PEP customer Maria Garcia..."
  - Note 80000000-0000-0000-0000-000000000005 (investigation): "Reviewed customer transaction history over past 12 months..."
  - Note 80000000-0000-0000-0000-000000000006 (recommendation): "Recommend independent officer review before final disposition..."

**CS-203 (PENDING_INFORMATION status):**
- Primary alert: ALT-2026-003 (40000000-0000-0000-0000-000000000003)
- 2 notes:
  - Note 80000000-0000-0000-0000-000000000007 (investigation): "Alert ALT-2026-003: Cross-border transaction USD 25,000..."
  - Note 80000000-0000-0000-0000-000000000008 (information_request): "Open information request issued 2026-11-21..."

---

## Progress Restoration Mechanism

The workspace endpoint supports progress restoration after information request resolution:

1. **Case Context Preservation:** All linked alerts, notes, requests, and timeline entries remain available even when case status transitions (e.g., from PENDING_INFORMATION back to INVESTIGATING)

2. **Timeline Continuity:** Audit events capture every state transition including return-to-investigation transitions, maintaining complete case history

3. **Note History:** All investigation notes remain visible chronologically, allowing investigators to resume work from where they left off after information request responses are received

4. **Blocker State Tracking:** current_blocker_state field reflects open/overdue request status, enabling immediate eligibility check for status transitions

---

## Audit Trail

All note additions create audit events:

**Event Type:** NOTE_ADDED

**Details JSON:**
```json
{
  "note_id": "uuid",
  "note_category": "investigation",
  "note_text_length": 142
}
```

**Fields Captured:**
- entity_type: "CASE"
- entity_id: case_id
- action_type: "NOTE_ADDED"
- actor_user_id: author_user_id
- actor_role: user role from auth context
- correlation_id: from X-Correlation-ID request header
- occurred_at_utc: timestamp

---

## Example Flows

### Adding Investigation Note
```bash
POST /api/v1/cases/50000000-0000-0000-0000-000000000001/notes
Headers:
  Authorization: Bearer <jwt-token>
  X-Correlation-ID: corr-123
  
Body:
{
  "note_category": "investigation",
  "note_text": "Reviewed customer background. Transaction appears legitimate."
}

Response 201:
{
  "note_id": "80000000-0000-0000-0000-000000000009",
  "case_id": "50000000-0000-0000-0000-000000000001",
  "note_category": "investigation",
  "note_text": "Reviewed customer background. Transaction appears legitimate.",
  "author_user_id": "00000000-0000-0000-0000-000000000001",
  "authored_at_utc": "2026-11-22T15:30:00Z"
}
```

### Retrieving Case Workspace
```bash
GET /api/v1/cases/50000000-0000-0000-0000-000000000001/workspace
Headers:
  Authorization: Bearer <jwt-token>
  
Response 200:
{
  "case_id": "50000000-0000-0000-0000-000000000001",
  "case_ref": "CS-201",
  "status": "OPEN",
  "linked_alerts": {"items": [...], "total": 2},
  "notes": {"items": [...], "total": 4},
  "evidence_gaps": {"items": [], "total": 0},
  "timeline_entries": {"items": [...], "total": 3}
}
```

---

## Acceptance Criteria Coverage

✅ **FR-007:** The system provides a narrative note area in the case workspace
- POST /api/v1/cases/{caseId}/notes endpoint implemented
- Saving a note captures author identity from auth context and authored_at_utc timestamp
- Notes remain available through GET workspace endpoint for independent officer review
- Multiple note entries supported without overwriting (notes ordered by authored_at_utc DESC)
- Note categories (investigation, recommendation, information_request, response, closure) remain distinguishable in history via note_category field

✅ **FR-012:** Progress restoration after information request resolution
- When open request is resolved, workspace endpoint reflects updated request state immediately
- Case can move from PENDING_INFORMATION back to INVESTIGATING status after blocking requests resolved
- Activity timeline shows return-to-investigation transition via audit events with action_type transitions
- Complete case context (alerts, notes, timeline) preserved through status transitions

---

## Testing

Run acceptance checks:
```bash
cd /repos/aml-transaction-monitoring/backend
alembic upgrade head
python app/seed.py
.venv/bin/python -m pytest tests/test_case_service.py::test_add_note -v
.venv/bin/python -m pytest tests/test_case_workspace.py -v
```

Expected results:
- Migration 005 creates case_notes table successfully
- Seed creates 8 sample notes across 3 cases
- test_add_note verifies note creation with audit event
- test_get_case_workspace verifies workspace aggregation with {items, total} structure
- test_get_case_workspace_not_found verifies 404 handling
