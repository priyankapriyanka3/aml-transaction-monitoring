# TASK-6 Handoff: Backend Feature B4 - Case Status Transitions and Information Request Issuance

## Implementation Summary

This task implements case status transitions with state machine validation and information request issuance functionality. The implementation adds:

1. Case status transition endpoint with validation
2. Information request creation endpoint
3. Information request response recording endpoint  
4. Information request listing by case
5. Automated case status transitions on request issuance/response
6. Complete audit trail for all operations
7. Unit and integration tests

## API Endpoints Implemented

All endpoints are mounted under `/api/v1` prefix and require JWT bearer authentication.

### POST /api/v1/cases/{case_id}/status-transitions

Transition case to new status with state machine validation.

**Valid State Transitions:**
- INVESTIGATING → PENDING_INFORMATION (on information request issuance)
- INVESTIGATING → REVIEW_READY (on recommendation submission + readiness pass)
- PENDING_INFORMATION → INVESTIGATING (on information response received)
- REVIEW_READY → SUBMITTED_FOR_REVIEW (on handoff submission)

**Request Body:**
```json
{
  "new_status": "PENDING_INFORMATION",
  "reason": "Information request issued",
  "trigger_event": "IR-001 created"
}
```

**Success Response (200):**
```json
{
  "case_id": "case-001",
  "previous_status": "INVESTIGATING",
  "new_status": "PENDING_INFORMATION",
  "transitioned_by_user_id": "usr-001",
  "transitioned_at": "2026-11-21T10:30:00.000Z",
  "trigger_event": "IR-001 created"
}
```

**Error Responses:**
- 404: Case not found
- 409: Invalid transition for current status

### POST /api/v1/information-requests

Create information request and automatically transition case to PENDING_INFORMATION.

**Request Body:**
```json
{
  "case_id": "case-CS-001",
  "recipient_channel": "EMAIL",
  "requested_summary": "Please provide supporting invoices and shipping documents for transaction txn-001",
  "rationale": "Need to verify legitimacy of large cross-border payment to Eastern Trade Corp",
  "due_at": "2026-11-28T12:00:00.000Z"
}
```

**Validation Rules:**
- `requested_summary`: minimum 10 characters
- `rationale`: minimum 10 characters
- `due_at`: must be future timestamp
- `recipient_channel`: must be EMAIL, PORTAL, or OPERATIONS_QUEUE

**Success Response (201):**
```json
{
  "information_request_id": "IR-001",
  "case_id": "case-CS-001",
  "status": "OPEN",
  "due_at": "2026-11-28T12:00:00.000Z",
  "created_at": "2026-11-21T10:30:00.000Z",
  "case_status_after_create": "PENDING_INFORMATION"
}
```

**Error Responses:**
- 404: Case not found
- 422: Validation failure (requested_summary too short, due_at not future, etc.)

### GET /api/v1/information-requests?case_id={case_id}

List all information requests for a case with computed SLA fields.

**Query Parameters:**
- `case_id` (required): Case ID to filter by

**Success Response (200):**
```json
[
  {
    "information_request_id": "IR-002",
    "case_id": "case-CS-001",
    "recipient_channel": "PORTAL",
    "requested_summary": "Provide detailed breakdown of beneficial ownership structure",
    "rationale": "Enhanced due diligence required",
    "status": "OPEN",
    "due_at": "2026-11-19T12:00:00.000Z",
    "days_remaining": -2,
    "is_overdue": true,
    "response_summary": null,
    "response_channel": null,
    "response_received_at": null,
    "created_by_user_id": "usr-001",
    "created_at": "2026-11-20T10:00:00.000Z"
  },
  {
    "information_request_id": "IR-001",
    "case_id": "case-CS-001",
    "recipient_channel": "EMAIL",
    "requested_summary": "Request copy of invoices and shipping documents",
    "rationale": "Need to verify legitimacy",
    "status": "OPEN",
    "due_at": "2026-11-24T12:00:00.000Z",
    "days_remaining": 2,
    "is_overdue": false,
    "response_summary": null,
    "response_channel": null,
    "response_received_at": null,
    "created_by_user_id": "usr-001",
    "created_at": "2026-11-20T08:00:00.000Z"
  }
]
```

**Note:** Results returned newest first (created_at DESC).

### POST /api/v1/information-requests/{information_request_id}/record-response

Record response to information request and transition case back to INVESTIGATING.

**Request Body:**
```json
{
  "response_summary": "All requested documents have been provided via secure portal",
  "received_at": "2026-11-21T10:00:00.000Z",
  "response_channel": "PORTAL"
}
```

**Validation Rules:**
- `response_summary`: minimum 10 characters
- `received_at`: cannot be in future
- Request status must be OPEN

**Success Response (200):**
```json
{
  "information_request_id": "IR-001",
  "status": "RESPONDED",
  "response_received_at": "2026-11-21T10:00:00.000Z",
  "case_status_after_response": "INVESTIGATING"
}
```

**Error Responses:**
- 404: Information request not found
- 422: Validation failure or request not in OPEN status

## State Machine Validation

The case status transition endpoint enforces the following state machine:

```
INVESTIGATING
  ├→ PENDING_INFORMATION (on information request issuance)
  └→ REVIEW_READY (on recommendation submission + readiness pass)

PENDING_INFORMATION
  └→ INVESTIGATING (on information response received)

REVIEW_READY
  └→ SUBMITTED_FOR_REVIEW (on handoff submission)
```

Invalid transitions return 409 Conflict with error message indicating valid transitions from current state.

## Audit Trail

All operations create corresponding audit events:

- **CASE_STATUS_CHANGED**: Created on status transition with previous_status, new_status, reason, trigger_event
- **INFORMATION_REQUEST_CREATED**: Created on request issuance with request details and case status transition
- **INFORMATION_REQUEST_RESPONSE_RECORDED**: Created on response recording with response details and case status transition

## Seed Data

The seed script creates 3 sample information requests:

### IR-001 (Open, Not Overdue)
- **Case:** CS-001
- **Status:** OPEN
- **Channel:** EMAIL
- **Summary:** "Request copy of invoices and shipping documents for transaction txn-001"
- **Rationale:** "Need to verify legitimacy of large cross-border payment"
- **Due:** 3 days from now (not overdue)

### IR-002 (Open, Overdue)
- **Case:** CS-001  
- **Status:** OPEN
- **Channel:** PORTAL
- **Summary:** "Provide detailed breakdown of beneficial ownership structure for Acme Global Trading Ltd"
- **Rationale:** "Enhanced due diligence required for high-risk customer"
- **Due:** 2 days ago (overdue)

### IR-003 (Responded)
- **Case:** CS-002
- **Status:** RESPONDED
- **Channel:** EMAIL
- **Summary:** "Submit quarterly investment reports and portfolio statements for Q3 and Q4"
- **Rationale:** "Verify transaction pattern consistency with normal fund operations"
- **Response:** "Investment reports provided. Confirms portfolio rebalancing activity. All transactions legitimate and consistent with fund strategy."
- **Received:** 5 days after creation

## Testing

### Unit Tests (test_status_transition_service.py)
- ✓ Valid transitions (INVESTIGATING→PENDING_INFORMATION, INVESTIGATING→REVIEW_READY, etc.)
- ✓ Invalid transition validation (returns ValueError with clear message)
- ✓ Case not found handling
- ✓ Audit event creation

### Unit Tests (test_information_request_service.py)
- ✓ Request creation with case transition
- ✓ due_at future validation
- ✓ Response recording with case transition
- ✓ received_at not future validation
- ✓ Days remaining calculation
- ✓ Overdue detection
- ✓ Non-OPEN request rejection

### Integration Tests (test_information_request_integration.py)
- ✓ POST /api/v1/information-requests endpoint
- ✓ GET /api/v1/information-requests?case_id=X endpoint
- ✓ POST /api/v1/information-requests/{id}/record-response endpoint
- ✓ POST /api/v1/cases/{id}/status-transitions endpoint
- ✓ Validation error handling
- ✓ Complete workflow: create request → list → record response
- ✓ Case status transitions

## Files Created/Modified

**Created:**
- `backend/app/schemas/information_request_schemas.py` - Request/response schemas with validation
- `backend/app/repositories/information_request_repository.py` - Information request data operations
- `backend/app/services/information_request_service.py` - Request orchestration with case transitions
- `backend/app/routers/information_requests.py` - Information request endpoints
- `backend/tests/test_status_transition_service.py` - Status transition unit tests
- `backend/tests/test_information_request_service.py` - Information request unit tests
- `backend/tests/test_information_request_integration.py` - Integration tests
- `.handoff/TASK-6.md` - This handoff document

**Modified:**
- `backend/app/repositories/case_repository.py` - Added transition_status method
- `backend/app/services/case_service.py` - Added transition_status method with state machine validation
- `backend/app/routers/cases.py` - Added POST /api/v1/cases/{case_id}/status-transitions endpoint
- `backend/app/main.py` - Registered information_requests router
- `backend/app/seed.py` - Added 3 sample information requests (IR-001, IR-002, IR-003)

## Dependencies

No new dependencies added. Uses existing packages:
- pydantic for schema validation
- SQLAlchemy for ORM
- FastAPI for routing

## Next Steps

This task completes the backend support for case status transitions and information request workflows. The implementation is ready for:

1. Frontend UI integration (wireframe_04_information_requests.html)
2. Integration with case workspace tabs (Information Requests tab)
3. Decision blocker banner when open/overdue requests exist
4. Request history timeline display

## Notes

- All endpoints require authentication (JWT bearer token)
- Status transitions are validated against state machine before applying
- Information request creation automatically transitions case to PENDING_INFORMATION
- Response recording automatically transitions case back to INVESTIGATING
- SLA fields (days_remaining, is_overdue) are computed dynamically on each request
- All operations create corresponding audit events for complete traceability
- Seed data provides good coverage for testing: one open request, one overdue request, one responded request
