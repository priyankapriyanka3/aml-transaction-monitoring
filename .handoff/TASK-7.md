# TASK-7 Handoff: Backend Feature B5 - Recommendation Submission and Review Handoff

## Implementation Summary

Implemented recommendation submission and handoff packaging functionality for AML case investigations, enabling investigators to submit recommendations and prepare cases for officer review with readiness validation and four-eyes segregation.

## API Endpoints

### POST /api/v1/cases/{case_id}/recommendation
Submit investigation recommendation for review.

**Request:**
```json
{
  "recommendation_outcome": "SUBSTANTIATE | NO_FURTHER_ACTION | ESCALATE_FOR_REVIEW",
  "findings_summary": "string (min 50 chars)",
  "supporting_note_ids": ["string"]
}
```

**Response (200):**
```json
{
  "case_id": "string",
  "recommendation_state": "SUBMITTED",
  "recommendation_outcome": "string",
  "findings_summary": "string",
  "submitted_by_user_id": "string",
  "submitted_at": "datetime"
}
```

**Validation:**
- findings_summary must be at least 50 characters
- Case must have at least one linked alert
- No open or overdue information requests allowed
- Returns 422 for validation failures
- Returns 409 when readiness prerequisites incomplete

**Behavior:**
- Updates case.recommendation_state to "SUBMITTED"
- Updates case.recommendation_outcome and findings_summary
- Creates INVESTIGATION_RECOMMENDATION_SUBMITTED audit event
- Blocked by open/overdue information requests (returns 409)

### GET /api/v1/cases/{case_id}/handoff
Get handoff package for review preview.

**Response (200):**
```json
{
  "case_id": "string",
  "case_number": "string",
  "recommendation_outcome": "string | null",
  "findings_summary": "string | null",
  "linked_alerts": [{
    "alert_id": "string",
    "priority": "string",
    "risk_score": 0
  }],
  "key_evidence_summary": ["string"],
  "information_request_summary": [{
    "information_request_id": "string",
    "status": "string",
    "due_at": "datetime",
    "resolved_at": "datetime | null"
  }],
  "unresolved_issues": ["string"],
  "readiness": {
    "is_ready": false,
    "checklist_items": [{
      "code": "string",
      "label": "string",
      "passed": false,
      "detail": "string"
    }]
  },
  "officer_assignment": {
    "officer_user_id": "string | null",
    "officer_display_name": "string | null"
  }
}
```

**Readiness Checklist Items:**
1. `linked_evidence` - At least 1 linked alert
2. `investigation_notes` - Investigation documented
3. `recommendation` - Recommendation present
4. `findings_summary` - Findings summary present (min 50 chars)
5. `no_open_requests` - All information requests resolved

### POST /api/v1/cases/{case_id}/handoff
Submit case for officer review (handoff).

**Request:**
```json
{
  "officer_user_id": "string",
  "submission_comment": "string | null"
}
```

**Response (200):**
```json
{
  "case_id": "string",
  "status": "SUBMITTED_FOR_REVIEW",
  "handoff_submitted_at": "datetime",
  "handoff_submitted_by_user_id": "string",
  "officer_user_id": "string",
  "readiness_passed": true
}
```

**Validation:**
- Four-eyes: officer_user_id must differ from case.created_by_user_id
- All readiness checklist items must pass
- Returns 409 when readiness_passed=false
- Returns 409 for four-eyes violation

**Behavior:**
- Validates four-eyes segregation (officer != creator)
- Evaluates readiness checklist
- Updates case.handoff_officer_user_id
- Transitions case status to SUBMITTED_FOR_REVIEW
- Creates CASE_HANDOFF_SUBMITTED audit event

## Services Created

### ReadinessService (`backend/app/services/readiness_service.py`)
Evaluates case readiness for handoff with 5-item checklist:
- Linked evidence (at least 1 alert)
- Investigation notes (always passes - tracked separately)
- Recommendation present (non-null, non-empty outcome)
- Findings summary (min 50 chars)
- No open or overdue requests

### HandoffService (`backend/app/services/handoff_service.py`)
Assembles handoff package with:
- Case details and recommendation
- Linked alerts summary
- Key evidence summary
- Information request summary
- Unresolved issues list
- Readiness checklist evaluation
- Officer assignment (if set)

## Repository Updates

### CaseRepository
Added `save_recommendation(case, recommendation_outcome, findings_summary, actor_id)`:
- Updates recommendation_state to "SUBMITTED"
- Sets recommendation_outcome and findings_summary
- Updates updated_at timestamp
- Returns updated case

## Seed Data Updates

Added sample recommendation to CS-002:
- recommendation_state: "SUBMITTED"
- recommendation_outcome: "NO_FURTHER_ACTION"
- findings_summary: 407 characters (meets min 50 requirement)
- Added audit event: INVESTIGATION_RECOMMENDATION_SUBMITTED

CS-002 is now ready for handoff (no open/overdue requests, has recommendation).
CS-001 still has open/overdue requests (IR-001, IR-002) blocking handoff.

## Validation Rules

### Recommendation Submission
- findings_summary minimum 50 characters (422 if violated)
- At least 1 linked alert required (409 if violated)
- No open information requests (409 if violated)
- No overdue information requests (409 if violated)

### Handoff Submission
- Four-eyes: officer != case creator (409 if violated)
- All readiness items must pass (409 if any fail)
- Valid state transition: REVIEW_READY → SUBMITTED_FOR_REVIEW

## Test Coverage

### Unit Tests
- `test_recommendation_service.py` (4 tests):
  - Successful recommendation submission
  - Validates findings length (min 50 chars)
  - Requires linked alert
  - Blocked by open requests

- `test_readiness_service.py` (4 tests):
  - All criteria passed
  - No linked alerts fails
  - No recommendation fails
  - Open requests fail

- `test_handoff_service.py` (3 tests):
  - Successful package assembly
  - Shows unresolved issues when not ready
  - Multiple alerts aggregation

### Integration Tests (appended to test_case_integration.py)
- POST /api/v1/cases/{case_id}/recommendation success (200)
- POST /api/v1/cases/{case_id}/recommendation validates findings length (422)
- GET /api/v1/cases/{case_id}/handoff package success (200)
- POST /api/v1/cases/{case_id}/handoff submission success (200)

## State Machine Updates

No changes to existing state machine. Recommendation submission does NOT auto-transition case status. Handoff submission transitions:
- REVIEW_READY → SUBMITTED_FOR_REVIEW (on handoff submission)

## Audit Events

### INVESTIGATION_RECOMMENDATION_SUBMITTED
Created when recommendation submitted.
Payload: recommendation_outcome, findings_summary_length, recommendation_state, submitted_at

### CASE_HANDOFF_SUBMITTED
Created when case handed off to officer.
Payload: officer_user_id, submission_comment, readiness_passed, submitted_at

## Dependencies

Depends on TASK-6:
- Status transitions (REVIEW_READY → SUBMITTED_FOR_REVIEW)
- Information request endpoints (for readiness validation)
- Case repository methods

## Notes

- Recommendation submission is separate from status transition
- Handoff readiness is evaluated dynamically (not cached)
- Four-eyes validation prevents investigator from being their own reviewer
- Readiness checklist provides clear blocking reasons when not ready
- CS-002 in seed data is fully ready for handoff testing
- CS-001 blocked by open/overdue information requests (demonstrates blocking behavior)
