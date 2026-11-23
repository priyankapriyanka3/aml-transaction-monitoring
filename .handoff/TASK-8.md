# TASK-8 Backend Handoff: Decision Blocker Enforcement and Officer Review

## API Endpoints

### GET /api/v1/cases/{caseId}/officer-review
Retrieve officer review package for independent decision.

**Response (200):**
```json
{
  "case_id": "uuid",
  "case_ref": "CS-204",
  "status": "UNDER_REVIEW",
  "current_blocker_state": "NONE",
  "created_by_user_id": "uuid",
  "assigned_officer_user_id": "uuid",
  "created_at_utc": "ISO8601 datetime",
  "updated_at_utc": "ISO8601 datetime",
  "linked_alerts": [
    {
      "alert_id": "uuid",
      "alert_ref": "ALT-2026-001",
      "priority": "CRITICAL",
      "risk_score": 95,
      "is_primary": true,
      "linked_at_utc": "ISO8601 datetime"
    }
  ],
  "notes": [
    {
      "note_id": "uuid",
      "note_category": "investigation",
      "note_text": "Investigation narrative...",
      "author_user_id": "uuid",
      "authored_at_utc": "ISO8601 datetime"
    }
  ],
  "requests": [
    {
      "request_id": "uuid",
      "request_ref": "IR-001",
      "status": "RESOLVED",
      "target_party": "Customer operations",
      "reason_text": "Request clarification...",
      "due_at_utc": "ISO8601 datetime",
      "response_summary": "Customer provided documentation...",
      "response_received_at_utc": "ISO8601 datetime"
    }
  ],
  "rule_snapshots": [
    {
      "snapshot_id": "uuid",
      "rule_code": "RULE-LARGE-TXN",
      "rule_name": "Large Transaction Monitoring",
      "rule_version": "v3.2",
      "outcome": "MATCH",
      "condition_text": "amount > 50000 AND risk_score > 80"
    }
  ],
  "blocker_state": "NONE",
  "is_conflicted_officer": false
}
```

**Errors:**
- `403 Forbidden` - Current user is case creator (four-eyes violation)
- `404 Not Found` - Case not found
- `401 Unauthorized` - Not authenticated

**Behavior:**
- Returns complete officer review package with case summary, linked alerts, investigation notes, information request history, and rule snapshots
- Derives blocker state from information requests (OPEN_REQUESTS if any request.status==OPEN, OVERDUE_REQUESTS if any request.status!=RESOLVED and due_at_utc < now)
- Checks if current user is case creator (four-eyes conflict)
- Returns 403 if current user is case creator
- Used by Screen 6 (Officer Review) to display package before decision entry

### POST /api/v1/cases/{caseId}/decision
Record final officer decision with mandatory rationale.

**Request:**
```json
{
  "outcome": "APPROVE|REJECT|ESCALATE|FALSE_POSITIVE",
  "rationale": "Detailed rationale text explaining the decision..."
}
```

**Response (201):**
```json
{
  "decision_id": "uuid",
  "case_id": "uuid",
  "outcome": "APPROVE",
  "rationale": "All evidence reviewed. Transaction is legitimate...",
  "deciding_officer_user_id": "uuid",
  "recorded_at_utc": "ISO8601 datetime",
  "immutable_hash": "sha256-hash"
}
```

**Headers:**
- `Authorization: Bearer <token>` (required)
- `X-Correlation-ID: <correlation-id>` (optional, generated if not provided)

**Errors:**
- `409 Conflict` - Decision blocked by open/overdue requests
- `403 Forbidden` - Officer is case creator (four-eyes violation)
- `422 Unprocessable Entity` - Rationale missing or invalid outcome
- `404 Not Found` - Case not found
- `401 Unauthorized` - Not authenticated

**Behavior:**
- Validates officer != case creator (four-eyes rule)
- Validates no open or overdue requests exist (blocker enforcement)
- Validates rationale is not empty
- Validates outcome is one of: APPROVE, REJECT, ESCALATE, FALSE_POSITIVE
- Generates immutable hash from case_id + outcome + rationale + timestamp
- Transitions case status based on outcome (APPROVED, REJECTED, ESCALATED, FALSE_POSITIVE)
- Sets case blocker_state to NONE
- Emits DECISION_RECORDED audit event
- Decision is immutable once recorded

## Blocker State Values

### NONE
No blockers exist. Case ready for decision.

### OPEN_REQUESTS
At least one information request has status == OPEN. Decision blocked until all requests resolved.

### OVERDUE_REQUESTS
At least one information request has status != RESOLVED and due_at_utc < now. Decision blocked until overdue requests resolved.

## Blocker Enforcement Rules

1. **UI-level blocker warning**: Frontend displays blocker banner when blocker_state != NONE
2. **Backend enforcement**: Decision endpoint rejects attempts (409) when blocker_state != NONE, even if UI bypassed
3. **Blocker derivation logic**:
   - Check all information_requests for case
   - If any request.status == OPEN: blocker_state = OPEN_REQUESTS
   - Else if any request.status != RESOLVED AND request.due_at_utc < now: blocker_state = OVERDUE_REQUESTS
   - Else: blocker_state = NONE
4. **Four-eyes enforcement**: Decision endpoint rejects if officer_user_id == case.created_by_user_id (403)
5. **Mandatory rationale**: Decision endpoint rejects if rationale is empty or whitespace-only (422)

## Seed Data

### Cases Ready for Officer Decision
- **CS-204** (`50000000-0000-0000-0000-000000000004`)
  - Status: UNDER_REVIEW
  - Created by: Investigator 1 (`00000000-0000-0000-0000-000000000001`)
  - Assigned to: Officer (`00000000-0000-0000-0000-000000000002`)
  - Blocker state: NONE
  - No open requests
  - Ready for decision

### Cases Blocked by Open Request
- **CS-205** (`50000000-0000-0000-0000-000000000005`)
  - Status: UNDER_REVIEW
  - Created by: Investigator 2 (`00000000-0000-0000-0000-000000000005`)
  - Assigned to: Officer (`00000000-0000-0000-0000-000000000002`)
  - Blocker state: OPEN_REQUESTS
  - Has open request IR-004 (due +2 days)
  - Decision blocked

## New Files

### Repositories
- `app/repositories/readiness_repository.py` - Blocker state derivation and four-eyes conflict checking

### Services
- `app/services/decision_service.py` - Officer review package assembly and decision recording with enforcement

### Schemas
- `app/schemas/review_schemas.py` - OfficerReviewPackageResponse, RecordDecisionRequest, DecisionRecordedResponse

### Routers
- `app/routers/decisions.py` - GET /api/v1/cases/{caseId}/officer-review, POST /api/v1/cases/{caseId}/decision

### Tests
- `tests/test_blocker_enforcement.py` - Blocker state derivation and four-eyes conflict tests
- `tests/test_officer_review.py` - Officer review endpoint and decision recording tests

## Workflow Flows

### Officer Review Flow
1. Officer navigates to Screen 6 (Officer Review) for assigned case
2. Frontend calls GET /api/v1/cases/{caseId}/officer-review
3. Backend checks if current user is case creator (403 if true)
4. Backend assembles officer review package:
   - Case summary
   - Linked alerts (with primary flag)
   - Investigation notes (ordered by authored_at_utc DESC)
   - Information requests (with response status)
   - Rule snapshots from primary alert
5. Backend derives blocker state from information requests
6. Backend checks if officer is conflicted (is_conflicted_officer flag)
7. Backend returns complete package with blocker_state and is_conflicted_officer
8. Frontend displays package with blocker warning if blocker_state != NONE

### Decision Recording Flow
1. Officer reviews package on Screen 6
2. Officer selects outcome (APPROVE, REJECT, ESCALATE, FALSE_POSITIVE)
3. Officer enters mandatory rationale text
4. Frontend calls POST /api/v1/cases/{caseId}/decision
5. Backend validates:
   - Officer != case creator (403 if same)
   - No open/overdue requests (409 if exist)
   - Rationale not empty (422 if empty)
   - Outcome is valid (422 if invalid)
6. Backend generates immutable hash (SHA-256 of case_id + outcome + rationale + timestamp)
7. Backend transitions case status based on outcome
8. Backend emits DECISION_RECORDED audit event
9. Backend returns 201 with decision details including immutable_hash
10. Frontend shows success confirmation

### Blocker Enforcement Flow
1. Officer attempts decision while open/overdue requests exist
2. Frontend shows blocker warning banner (UI-level prevention)
3. If UI bypassed, backend rejects with 409 Conflict
4. Error message explains specific blocker: "Cannot record decision while open requests exist" or "Cannot record decision while overdue requests exist"
5. Officer must resolve all requests before decision allowed
6. Once requests resolved, blocker_state becomes NONE and decision allowed

## Integration Points

### Screen 6 (Officer Review & Decision)
- Calls GET /api/v1/cases/{caseId}/officer-review to load package
- Displays blocker warning banner if blocker_state != NONE
- Shows "Return for investigation" alternative action (not implemented in this task)
- Disables "Record decision" button until outcome selected and rationale entered
- Calls POST /api/v1/cases/{caseId}/decision when decision submitted
- Handles 409 errors by showing blocker message
- Handles 403 errors by showing four-eyes conflict message
- Handles 422 errors by showing validation message

### Compliance Requirements
- FR-010: Blocker enforcement prevents decision while open/overdue requests exist
- FR-016: Explicit decision options (APPROVE, REJECT, ESCALATE, FALSE_POSITIVE) with mandatory rationale
- FR-019: Four-eyes rule prevents case creator from deciding own case
- FR-020: Immutable audit trail with DECISION_RECORDED events

## Error Response Examples

### 409 Conflict - Open Requests Blocker
```json
{
  "detail": "Cannot record decision while open requests exist"
}
```

### 403 Forbidden - Four-Eyes Violation
```json
{
  "detail": "Case creator cannot decide own case"
}
```

### 422 Unprocessable Entity - Missing Rationale
```json
{
  "detail": "Rationale is required"
}
```

### 422 Unprocessable Entity - Invalid Outcome
```json
{
  "detail": "Invalid outcome. Must be one of: APPROVE, REJECT, ESCALATE, FALSE_POSITIVE"
}
```
