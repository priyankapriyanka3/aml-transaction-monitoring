# TASK-9 Handoff: Information Request Response Recording and Readiness Verification

## Implemented Endpoints

### Information Request Endpoints

**GET /api/v1/cases/{caseId}/requests/{requestId}**
- Returns information request details including blocker state
- Response shape:
  ```json
  {
    "request_id": "uuid",
    "request_ref": "IR-001",
    "case_id": "uuid",
    "gap_id": "uuid",
    "target_party": "string",
    "delivery_channel": "string",
    "reason_text": "string",
    "due_at_utc": "2026-11-25T10:00:00Z",
    "status": "OPEN" | "OVERDUE" | "RESPONDED" | "RESOLVED",
    "created_by_user_id": "uuid",
    "response_summary": "string" | null,
    "response_received_at_utc": "2026-11-22T14:30:00Z" | null,
    "created_at_utc": "2026-11-20T10:00:00Z",
    "updated_at_utc": "2026-11-22T14:30:00Z",
    "blocker_state": "NONE" | "OPEN_REQUESTS" | "OVERDUE_REQUESTS"
  }
  ```
- Blocker state reflects case-level decision blocking status
- 404 if request not found or not in specified case
- 401 if not authenticated

**POST /api/v1/cases/{caseId}/requests/{requestId}/response**
- Records response to an information request
- Request body:
  ```json
  {
    "response_summary": "string (required)",
    "received_at_utc": "2026-11-22T14:30:00Z (required)"
  }
  ```
- Response shape:
  ```json
  {
    "request_id": "uuid",
    "status": "RESPONDED",
    "response_summary": "string",
    "response_received_at_utc": "2026-11-22T14:30:00Z"
  }
  ```
- Updates request status to RESPONDED
- Recalculates case blocker_state
- Emits RESPONSE_RECORDED audit event with correlation_id
- 422 if response_summary or received_at_utc missing
- 404 if request not found
- 401 if not authenticated

### Readiness Endpoints

**GET /api/v1/cases/{caseId}/readiness**
- Returns readiness checklist and package summary
- Response shape:
  ```json
  {
    "checklist": [
      {
        "name": "linked_evidence",
        "complete": true,
        "details": "1 alert(s) linked"
      },
      {
        "name": "investigation_notes",
        "complete": true,
        "details": "2 note(s) recorded"
      },
      {
        "name": "responses_reviewed",
        "complete": true,
        "details": "1 of 1 requests reviewed"
      },
      {
        "name": "no_open_requests",
        "complete": true,
        "details": "No open or overdue requests"
      }
    ],
    "package_summary": {
      "alert_count": 1,
      "note_count": 2,
      "request_count": 1,
      "evidence_count": 1
    }
  }
  ```
- Checklist item definitions:
  - **linked_evidence**: Complete if >= 1 linked alert
  - **investigation_notes**: Complete if >= 1 note recorded
  - **responses_reviewed**: Complete if all requests have status != OPEN
  - **no_open_requests**: Complete if no requests with status OPEN or OVERDUE
- Package summary provides counts for case package elements
- 404 if case not found
- 401 if not authenticated

## Validation Rules

### Response Recording Validation
- `response_summary` must be non-empty string (trimmed)
- `received_at_utc` must be provided (cannot be null)
- Both fields are required (422 if missing)

### Blocker State Derivation Logic
The blocker state is calculated from information requests:
- **OPEN_REQUESTS**: At least one request with status == OPEN
- **OVERDUE_REQUESTS**: At least one request with status != RESOLVED and due_at_utc < now
- **NONE**: No blockers present

Priority: OPEN_REQUESTS checked first, then OVERDUE_REQUESTS, then NONE.

### Readiness Checklist Logic
Each checklist item has specific completion criteria:
1. **linked_evidence**: Counts case_alert_links, complete if count >= 1
2. **investigation_notes**: Counts case_notes, complete if count >= 1
3. **responses_reviewed**: Counts OPEN requests, complete if count == 0
4. **no_open_requests**: Counts OPEN + OVERDUE requests, complete if both == 0

## Seed Data

### Information Request Seed Records
- **IR-001** (a0000000-0000-0000-0000-000000000001): CS-201, OPEN, future due date
- **IR-002** (a0000000-0000-0000-0000-000000000002): CS-202, OVERDUE, past due date
- **IR-003** (a0000000-0000-0000-0000-000000000003): CS-203, OPEN, near-future due date
- **IR-004** (a0000000-0000-0000-0000-000000000004): CS-205, OPEN, blocks officer decision
- **IR-005** (a0000000-0000-0000-0000-000000000005): CS-204, RESPONDED with summary and received date

### Sample RESPONDED Request (IR-005)
```json
{
  "request_id": "a0000000-0000-0000-0000-000000000005",
  "request_ref": "IR-005",
  "case_id": "50000000-0000-0000-0000-000000000004",
  "status": "RESPONDED",
  "response_summary": "Customer provided comprehensive documentation including signed contracts, invoices, and beneficiary company registration. All materials have been reviewed and appear legitimate. Business relationship is established and ongoing.",
  "response_received_at_utc": "2026-11-22T08:00:00Z"
}
```

## Data Flow

### Response Recording Flow
1. User calls POST /api/v1/cases/{caseId}/requests/{requestId}/response
2. InformationRequestService validates request exists
3. InformationRequestRepository updates request:
   - Sets response_summary
   - Sets response_received_at_utc
   - Changes status to RESPONDED
   - Updates updated_at_utc timestamp
4. ReadinessRepository recalculates case blocker_state
5. CaseRepository updates case current_blocker_state field
6. AuditService emits RESPONSE_RECORDED event with actor, timestamp, correlation_id
7. Database transaction commits
8. Response returned to client

### Readiness Checklist Derivation Flow
1. User calls GET /api/v1/cases/{caseId}/readiness
2. ReadinessService validates case exists
3. ReadinessRepository queries checklist state:
   - Count linked alerts from case_alert_links
   - Count notes from case_notes
   - Count total requests from information_requests
   - Count OPEN requests (status == OPEN)
   - Count OVERDUE requests (status != RESOLVED and due_at_utc < now)
4. ReadinessService builds 4 checklist items with completion status
5. ReadinessService builds package summary with counts
6. ReadinessProjection returned to client

## Audit Events

### RESPONSE_RECORDED Event
Emitted when information request response is recorded:
```json
{
  "entity_type": "REQUEST",
  "entity_id": "request_id",
  "action_type": "RESPONSE_RECORDED",
  "actor_user_id": "uuid",
  "actor_role": "INVESTIGATOR",
  "correlation_id": "string",
  "details_json": {
    "request_ref": "IR-005",
    "case_id": "uuid",
    "status": "RESPONDED",
    "response_summary": "first 200 chars...",
    "received_at_utc": "2026-11-22T14:30:00Z"
  },
  "occurred_at_utc": "2026-11-22T14:30:00Z"
}
```

## Implementation Notes

### New Files Created
- `app/schemas/request_schemas.py` - Request/response schemas for information requests
- `app/schemas/readiness_schemas.py` - Readiness checklist schemas
- `app/services/readiness_service.py` - Readiness checklist derivation service
- `app/routers/requests.py` - Information request endpoints
- `app/routers/readiness.py` - Readiness checklist endpoints
- `tests/test_information_request_service.py` - Service tests for response recording
- `tests/test_readiness_service.py` - Service tests for checklist derivation

### Modified Files
- `app/repositories/information_request_repository.py` - Added record_response method
- `app/repositories/readiness_repository.py` - Added get_checklist_state method
- `app/services/information_request_service.py` - Added record_response method
- `app/main.py` - Registered readiness router
- `app/seed.py` - Added IR-005 RESPONDED request seed data

### Database Changes
No new migrations required. All tables already exist from previous tasks.

### Testing Coverage
- InformationRequestService.record_response: 2 tests (success, not found)
- ReadinessService.derive_checklist: 3 tests (all complete, with blockers, not found)
- All tests verify proper status updates, blocker state recalculation, and audit events

## Frontend Integration Notes

### Response Recording Screen Flow
1. Display request details from GET /api/v1/cases/{caseId}/requests/{requestId}
2. Show blocker warning banner if blocker_state != NONE
3. Capture response_summary (required text field)
4. Capture received_at_utc (required date picker, cannot be future date)
5. Submit to POST /api/v1/cases/{caseId}/requests/{requestId}/response
6. Handle 422 validation errors for missing fields
7. On success, navigate back to case workspace or requests list

### Readiness Checklist Screen Flow
1. Fetch readiness from GET /api/v1/cases/{caseId}/readiness
2. Display 4 checklist items with complete/incomplete status
3. Show green checkmark icon for complete items
4. Show outline circle icon for incomplete items
5. Display package summary counts (alerts, notes, requests, evidence)
6. Enable "Share for officer review" button only when all checklist items complete
7. Package summary is collapsible or expandable section

### Blocker State Handling
- When blocker_state == "OPEN_REQUESTS": Show "X open requests — decision blocked"
- When blocker_state == "OVERDUE_REQUESTS": Show "X overdue requests — decision blocked"
- When blocker_state == "NONE": Hide blocker warning banner
- Blocker banner uses warning colors and ARIA live region semantics

## Known Constraints

- Response summary and received date are both required (not optional)
- Blocker state is derived in real-time (not cached)
- Readiness checklist is derived in real-time (not pre-calculated)
- Checklist completion does not guarantee no blockers (separate check required)
- Recording a response immediately recalculates case blocker_state
- Only OPEN and OVERDUE requests block decisions (RESPONDED and RESOLVED do not)
