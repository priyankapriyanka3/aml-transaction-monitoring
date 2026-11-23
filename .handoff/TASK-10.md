# TASK-10: Backend Feature B8 - Independent Officer Assignment and Final Decision Recording

## Implemented Endpoints

### GET /api/v1/cases/{caseId}/officer-review
Retrieves the officer review package for a case.

**Request:** None (authenticated via Bearer token)

**Response (200 OK):**
```json
{
  "case_id": "uuid",
  "case_ref": "CS-204",
  "status": "UNDER_REVIEW",
  "blocker_state": "NONE",
  "is_conflicted_officer": false,
  "linked_alerts": [
    {
      "alert_id": "uuid",
      "alert_ref": "ALT-2026-004",
      "is_primary": true
    }
  ],
  "notes": [
    {
      "note_id": "uuid",
      "note_text": "Investigation complete...",
      "author_user_id": "uuid",
      "authored_at_utc": "2026-11-22T14:30:00Z"
    }
  ],
  "rule_snapshots": [
    {
      "snapshot_id": "uuid",
      "rule_name": "High Value Transaction Rule",
      "rule_version": "v3.2",
      "outcome": "MATCH"
    }
  ]
}
```

**Error Responses:**
- 403: User is case creator (four-eyes enforcement)
- 404: Case not found

**Validation:**
- Validates current user != case creator (403 if violated)
- Returns `is_conflicted_officer` flag indicating if current user is case creator
- Returns `blocker_state` (NONE, OPEN_REQUESTS, OVERDUE_REQUESTS)
- Aggregates linked alerts, investigation notes, and rule snapshots

---

### POST /api/v1/cases/{caseId}/assign-officer
Assigns an independent officer to a case for final review.

**Request:**
```json
{
  "officer_user_id": "uuid"
}
```

**Response (200 OK):**
```json
{
  "assignment_id": "uuid",
  "case_id": "uuid",
  "officer_user_id": "uuid",
  "assigned_by_user_id": "uuid",
  "assigned_at_utc": "2026-11-22T14:30:00Z"
}
```

**Error Responses:**
- 404: Case not found
- 409: Four-eyes violation - officer cannot be case creator

**Validation:**
- Validates `officer_user_id` != `case.created_by_user_id` (four-eyes enforcement)
- Creates or updates `case_review_assignments` record (unique by case_id)
- Updates `case.assigned_officer_user_id` field
- Emits `OFFICER_ASSIGNED` audit event

---

### POST /api/v1/cases/{caseId}/share-for-review
Transitions case to UNDER_REVIEW status after validation checks.

**Request:** Empty body

**Response (200 OK):**
```json
{
  "case_id": "uuid",
  "status": "UNDER_REVIEW",
  "shared_at_utc": "2026-11-22T14:30:00Z"
}
```

**Error Responses:**
- 404: Case not found
- 409: Validation failure with specific reason:
  - "Cannot share for review: No linked alerts"
  - "Cannot share for review: No investigation notes"
  - "Cannot share for review: Open information requests remain"
  - "Cannot share for review: Overdue information requests remain"
  - "Cannot share for review: No officer assigned"
  - "Cannot share for review: Officer cannot be case creator"

**Validation (all must pass):**
1. At least 1 linked alert (`linked_alert_count >= 1`)
2. At least 1 investigation note (`note_count >= 1`)
3. No open requests (`open_request_count == 0`)
4. No overdue requests (`overdue_request_count == 0`)
5. Officer assigned (`case.assigned_officer_user_id != null`)
6. Officer != case creator (`case.assigned_officer_user_id != case.created_by_user_id`)

**Behavior:**
- Updates `case.status` to `UNDER_REVIEW`
- Emits `SHARED_FOR_REVIEW` audit event
- All validations checked at submission time (not cached)

---

### POST /api/v1/cases/{caseId}/decision
Records an immutable final decision on a case.

**Request:**
```json
{
  "outcome": "APPROVE|REJECT|ESCALATE|FALSE_POSITIVE|RETURN_FOR_INVESTIGATION",
  "rationale_text": "string (required, non-empty)",
  "rationale": "string (backward compatibility alias for rationale_text)"
}
```

**Note:** Either `rationale_text` or `rationale` field can be used in the request. Both map to the same field internally.

**Response (201 Created):**
```json
{
  "decision_id": "uuid",
  "case_id": "uuid",
  "deciding_officer_user_id": "uuid",
  "outcome": "APPROVE",
  "rationale_text": "Case approved after comprehensive review...",
  "rationale": "Case approved after comprehensive review...",
  "recorded_at_utc": "2026-11-22T14:30:00Z",
  "immutable_hash": "sha256-hash-64-chars"
}
```

**Note:** The response includes both `rationale_text` and `rationale` fields (same value) for backward compatibility.

**Error Responses:**
- 403: Four-eyes violation - officer cannot decide own case
- 404: Case not found
- 409: Decision blocked by open/overdue requests
- 422: Rationale text is required

**Validation:**
- Current user != `case.created_by_user_id` (403 if violated)
- No open/overdue requests - blocker_state must be `NONE` (409 if violated)
- `rationale_text` not empty/whitespace-only (422 if violated)

**Immutable Hash Computation:**
```
SHA-256 hash of: {case_id}|{outcome}|{rationale_text}|{recorded_at_utc}
```

**Behavior:**
- Creates immutable `case_decisions` record
- Updates `case.status` to outcome-mapped status:
  - `APPROVE` → `APPROVED`
  - `REJECT` → `REJECTED`
  - `ESCALATE` → `ESCALATED`
  - `FALSE_POSITIVE` → `FALSE_POSITIVE`
  - `RETURN_FOR_INVESTIGATION` → `RETURNED_FOR_INVESTIGATION`
- Emits `DECISION_RECORDED` audit event

---

### GET /api/v1/cases/{caseId}/readiness (Extended)
Now returns `eligible_officers` list in addition to checklist and package summary.

**Response:**
```json
{
  "checklist": [
    {"name": "linked_evidence", "complete": true, "details": "2 alert(s) linked"},
    {"name": "investigation_notes", "complete": true, "details": "3 note(s) recorded"},
    {"name": "responses_reviewed", "complete": true, "details": "2 of 2 requests reviewed"},
    {"name": "no_open_requests", "complete": true, "details": "No open or overdue requests"}
  ],
  "package_summary": {
    "alert_count": 2,
    "note_count": 3,
    "request_count": 2,
    "evidence_count": 2
  },
  "eligible_officers": [
    {
      "user_id": "uuid",
      "display_name": "Bob Officer",
      "email": "officer@example.com"
    }
  ]
}
```

**Eligible Officers Logic:**
- Returns all users with `role == "OFFICER"` and `is_active == true`
- Excludes `case.created_by_user_id` (four-eyes enforcement)
- Ordered by `display_name` ascending

---

## Database Schema

### case_review_assignments
```sql
CREATE TABLE case_review_assignments (
  assignment_id UUID PRIMARY KEY,
  case_id UUID NOT NULL UNIQUE REFERENCES aml_cases(case_id),
  officer_user_id UUID NOT NULL REFERENCES users(user_id),
  assigned_by_user_id UUID NOT NULL REFERENCES users(user_id),
  assigned_at_utc TIMESTAMP NOT NULL
);
CREATE INDEX ix_case_review_assignments_case_id ON case_review_assignments(case_id);
```

### case_decisions
```sql
CREATE TABLE case_decisions (
  decision_id UUID PRIMARY KEY,
  case_id UUID NOT NULL REFERENCES aml_cases(case_id),
  deciding_officer_user_id UUID NOT NULL REFERENCES users(user_id),
  outcome VARCHAR(40) NOT NULL CHECK (outcome IN ('APPROVE', 'REJECT', 'ESCALATE', 'FALSE_POSITIVE', 'RETURN_FOR_INVESTIGATION')),
  rationale_text TEXT NOT NULL,
  recorded_at_utc TIMESTAMP NOT NULL,
  immutable_hash VARCHAR(128) NOT NULL
);
CREATE INDEX ix_case_decisions_case_id ON case_decisions(case_id);
```

---

## Seed Data

### Sample Cases

**CS-204** (Ready for officer decision):
- Status: `UNDER_REVIEW`
- Blocker state: `NONE`
- Officer assigned: Bob Officer (`00000000-0000-0000-0000-000000000002`)
- Created by: Alice Investigator (`00000000-0000-0000-0000-000000000001`)
- All checklist items complete
- No open/overdue requests
- Case ID: `50000000-0000-0000-0000-000000000004`

**CS-205** (Blocked by open request):
- Status: `UNDER_REVIEW`
- Blocker state: `OPEN_REQUESTS`
- Officer assigned: Bob Officer
- Has 1 OPEN information request (IR-004)
- Cannot record decision until request resolved
- Case ID: `50000000-0000-0000-0000-000000000005`

**CS-206** (Completed with decision):
- Status: `APPROVED`
- Blocker state: `NONE`
- Officer: Bob Officer
- Decision recorded with outcome `APPROVE`
- Decision ID: `c0000000-0000-0000-0000-000000000001`
- Case ID: `50000000-0000-0000-0000-000000000006`

### Information Requests
- **IR-005** (RESPONDED): Demonstrates response recording feature
  - Case: CS-204
  - Status: `RESPONDED`
  - Response summary included
  - Request ID: `a0000000-0000-0000-0000-000000000005`

### Officer Assignments
- Assignment for CS-204: `b0000000-0000-0000-0000-000000000001`
- Assignment for CS-206: `b0000000-0000-0000-0000-000000000002`

### Completed Decision
- Decision for CS-206: `c0000000-0000-0000-0000-000000000001`
  - Outcome: `APPROVE`
  - Immutable hash: SHA-256 of decision payload
  - Rationale: "After comprehensive review of all supporting documentation..."

---

## Four-Eyes Enforcement

### Validation Points

1. **Officer Assignment** (`POST /api/v1/cases/{caseId}/assign-officer`):
   - Backend validates `officer_user_id != case.created_by_user_id`
   - Returns 409 if violated

2. **Share for Review** (`POST /api/v1/cases/{caseId}/share-for-review`):
   - Backend validates `case.assigned_officer_user_id != case.created_by_user_id`
   - Returns 409 if violated

3. **Decision Recording** (`POST /api/v1/cases/{caseId}/decision`):
   - Backend validates `current_user.user_id != case.created_by_user_id`
   - Returns 403 if violated

4. **Eligible Officers** (`GET /api/v1/cases/{caseId}/readiness`):
   - Frontend receives eligible officers list excluding case creator
   - Frontend should disable/hide case creator from officer dropdown

### Enforcement Flow

```
1. Investigator creates case (case.created_by_user_id = investigator)
2. Investigator completes investigation
3. Investigator selects officer from eligible_officers list (excludes self)
4. POST /api/v1/cases/{caseId}/assign-officer validates officer != case creator
5. POST /api/v1/cases/{caseId}/share-for-review re-validates officer != case creator
6. Officer reviews case
7. POST /api/v1/cases/{caseId}/decision validates officer != case creator
```

---

## Blocker State Management

### Blocker States
- `NONE` - No blockers, decision can proceed
- `OPEN_REQUESTS` - At least one information request with status `OPEN`
- `OVERDUE_REQUESTS` - At least one request with status != `RESOLVED` and due_at_utc < now

### Blocker Enforcement
- Decision endpoint checks blocker state before recording
- Returns 409 with `OPEN_REQUESTS` or `OVERDUE_REQUESTS` in detail if blocked
- Share-for-review validates no open/overdue requests

### Blocker Resolution
- Blocker state recalculated when:
  - Information request created/updated
  - Request response recorded
  - Request status changed

---

## Audit Events

### OFFICER_ASSIGNED
```json
{
  "entity_type": "CASE",
  "entity_id": "case-uuid",
  "action_type": "OFFICER_ASSIGNED",
  "actor_user_id": "assigner-uuid",
  "actor_role": "INVESTIGATOR",
  "correlation_id": "correlation-uuid",
  "details_json": {
    "case_id": "case-uuid",
    "officer_user_id": "officer-uuid",
    "assigned_by_user_id": "assigner-uuid"
  }
}
```

### SHARED_FOR_REVIEW
```json
{
  "entity_type": "CASE",
  "entity_id": "case-uuid",
  "action_type": "SHARED_FOR_REVIEW",
  "actor_user_id": "sharer-uuid",
  "actor_role": "INVESTIGATOR",
  "correlation_id": "correlation-uuid",
  "details_json": {
    "case_id": "case-uuid",
    "status": "UNDER_REVIEW",
    "shared_at_utc": "2026-11-22T14:30:00Z"
  }
}
```

### DECISION_RECORDED
```json
{
  "entity_type": "CASE",
  "entity_id": "case-uuid",
  "action_type": "DECISION_RECORDED",
  "actor_user_id": "officer-uuid",
  "actor_role": "OFFICER",
  "correlation_id": "correlation-uuid",
  "details_json": {
    "case_id": "case-uuid",
    "decision_id": "decision-uuid",
    "outcome": "APPROVE",
    "recorded_at_utc": "2026-11-22T14:30:00Z"
  }
}
```

---

## Testing

### Test Files
- `tests/test_four_eyes_enforcement.py` - Four-eyes validation tests
- `tests/test_decision_service.py` - Decision service functionality tests
- `tests/test_decision_immutability.py` - Immutability and rationale tests

### Key Test Scenarios
1. Officer assignment prevents case creator assignment (409)
2. Decision recording prevents case creator decision (403)
3. Readiness endpoint excludes case creator from eligible officers
4. Share-for-review validates all checklist items
5. Share-for-review blocks without officer assignment
6. Decision recording creates immutable hash
7. Decision requires non-empty rationale (422)
8. Decision blocks with open requests (409)

---

## Frontend Integration Notes

### Officer Assignment Flow
1. GET `/api/v1/cases/{caseId}/readiness` - Get eligible officers list
2. Display officer dropdown populated from `eligible_officers` array
3. Case creator should NOT appear in dropdown (already excluded by backend)
4. POST `/api/v1/cases/{caseId}/assign-officer` with selected officer
5. Handle 409 error gracefully (should not occur if using eligible officers list)

### Share for Review Flow
1. Verify all 4 checklist items show `complete: true`
2. Enable "Share for review" button only when all items complete
3. POST `/api/v1/cases/{caseId}/share-for-review`
4. Handle 409 errors with specific failure messages to guide investigator

### Decision Recording Flow
1. Verify case status is `UNDER_REVIEW`
2. Check blocker state is `NONE` (no open/overdue requests)
3. Display decision selector: APPROVE, REJECT, ESCALATE, FALSE_POSITIVE
4. Require rationale text field (non-empty validation)
5. Disable "Record decision" button until outcome selected + rationale entered
6. POST `/api/v1/cases/{caseId}/decision`
7. Handle errors:
   - 403: Officer is case creator (should not occur with proper auth)
   - 409: Blocker present (display blocker reason to officer)
   - 422: Rationale missing (client-side validation should prevent)

### UI Validation Hints
- Rationale text field: `required`, `minlength=10`
- Officer dropdown: Exclude case creator from options
- Share button: Disabled until all checklist items `complete: true`
- Decision button: Disabled until outcome selected AND rationale non-empty

---

## Error Code Reference

| Code | Endpoint | Reason | User Action |
|------|----------|--------|-------------|
| 403  | `/decision` | Officer is case creator | Re-assign to different officer |
| 404  | All | Case not found | Verify case ID |
| 409  | `/assign-officer` | Officer is case creator | Select different officer from eligible list |
| 409  | `/share-for-review` | Validation failure | Complete missing checklist items |
| 409  | `/decision` | Open/overdue requests | Resolve requests before decision |
| 422  | `/decision` | Rationale missing | Provide mandatory rationale |
