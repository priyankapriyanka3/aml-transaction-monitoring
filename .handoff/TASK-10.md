# TASK-10 Handoff: Information Request Response and SLA Tracking

## Implemented Features

### 1. Information Request Response Recording
**Endpoint:** `POST /api/v1/information-requests/{information_request_id}/record-response`

**Already implemented in TASK-6**, now verified with additional seed data.

**Request Body:**
```json
{
  "response_summary": "string (min 10 chars)",
  "received_at": "ISO datetime (cannot be future)",
  "response_channel": "EMAIL | PORTAL | OPERATIONS_QUEUE"
}
```

**Response (200):**
```json
{
  "information_request_id": "IR-001",
  "status": "RESPONDED",
  "response_received_at": "2026-11-14T10:30:00Z",
  "case_status_after_response": "INVESTIGATING"
}
```

**Business Logic:**
- Validates response_summary (minimum 10 characters)
- Validates received_at is not in the future
- Validates request status is OPEN (returns 422 if not)
- Updates request status to RESPONDED
- Transitions case from PENDING_INFORMATION to INVESTIGATING
- Creates INFORMATION_REQUEST_RESPONSE_RECORDED audit event
- All operations in same transaction

**Validation Errors (422):**
- response_summary less than 10 characters
- received_at is in the future
- request status is not OPEN

---

### 2. Information Request List with SLA Tracking
**Endpoint:** `GET /api/v1/information-requests?case_id={case_id}`

**Already implemented in TASK-6**, now verified with seed data.

**Response (200):**
```json
[
  {
    "information_request_id": "IR-001",
    "case_id": "case-CS-001",
    "recipient_channel": "EMAIL",
    "requested_summary": "Request copy of invoices...",
    "rationale": "Need to verify legitimacy...",
    "status": "RESPONDED",
    "due_at": "2026-11-19T00:00:00Z",
    "days_remaining": null,
    "is_overdue": false,
    "response_summary": "Invoices provided...",
    "response_channel": "EMAIL",
    "response_received_at": "2026-11-17T14:20:00Z",
    "created_by_user_id": "usr-001",
    "created_at": "2026-11-14T10:00:00Z"
  }
]
```

**SLA Computation:**
- `days_remaining`: Computed as `(due_at - now).days` when status is OPEN, otherwise null
- `is_overdue`: True when `due_at < now AND status=OPEN`, otherwise false
- Requests returned in chronological order (created_at DESC, newest first)

**Overdue Detection:**
- A request is overdue when it remains OPEN and due_at has passed
- Responded requests (status=RESPONDED) are never marked overdue

---

### 3. Audit Events Retrieval
**Endpoint:** `GET /api/v1/audit-events`

**New implementation in TASK-10.**

**Query Parameters:**
- `entity_type` (optional): Filter by entity type (e.g., "case", "alert")
- `entity_id` (optional): Filter by specific entity ID
- `action_type` (optional): Filter by action type (e.g., "CASE_CREATED", "INFORMATION_REQUEST_RESPONSE_RECORDED")
- `limit` (optional, default=50, max=200): Number of events to return
- `offset` (optional, default=0): Number of events to skip

**Response (200):**
```json
{
  "items": [
    {
      "audit_event_id": "audit-007a",
      "entity_type": "case",
      "entity_id": "case-CS-001",
      "action_type": "INFORMATION_REQUEST_RESPONSE_RECORDED",
      "actor_user_id": "usr-001",
      "actor_role": "investigator",
      "correlation_id": "corr-005a",
      "occurred_at": "2026-11-17T14:20:00Z",
      "payload": {
        "information_request_id": "IR-001",
        "response_channel": "EMAIL",
        "received_at": "2026-11-17T14:20:00Z",
        "previous_status": "PENDING_INFORMATION",
        "new_status": "INVESTIGATING"
      }
    }
  ],
  "total_count": 11,
  "limit": 50,
  "offset": 0
}
```

**Features:**
- Supports pagination (limit/offset)
- Supports filtering by entity_type, entity_id, action_type
- Returns events ordered by occurred_at DESC (newest first)
- Requires authentication

---

### 4. Health/Readiness Endpoint
**Endpoint:** `GET /api/v1/health/ready`

**New implementation in TASK-10.**

**Response (200):**
```json
{
  "status": "ready",
  "app_version": "1.0.0",
  "database": "connected",
  "checked_at": "2026-11-21T10:30:45.123456Z"
}
```

**Features:**
- Accessible without authentication
- Performs database connection check via `SELECT 1`
- Returns "connected" if database is accessible, "error: {message}" otherwise
- Includes ISO timestamp of check
- Can be used by orchestrators (Kubernetes, Docker Compose) for readiness probes

---

## Database Changes

### Seed Data Updates
Updated `/repos/aml-transaction-monitoring/backend/app/seed.py`:

**Information Requests:**
- `IR-001`: RESPONDED (was OPEN) - response recorded with summary "Invoices and shipping documents provided"
- `IR-002`: OPEN and OVERDUE (due 2 days ago)
- `IR-003`: RESPONDED (unchanged)

**Audit Events:**
- Added `audit-007a`: INFORMATION_REQUEST_RESPONSE_RECORDED event for IR-001 response

**Summary Output:**
```
- Information Requests: 3 (IR-001 responded, IR-002 overdue, IR-003 responded)
- Audit Events: 11 (includes IR-001 response and recommendation submission)
- SLA tracking: IR-002 overdue (due 2 days ago), IR-001 and IR-003 responded
```

---

## Service/Repository Changes

### New Files Created
1. `/repos/aml-transaction-monitoring/backend/app/routers/audit_events.py`
   - GET /api/v1/audit-events endpoint with filtering and pagination

2. `/repos/aml-transaction-monitoring/backend/app/routers/health.py`
   - GET /api/v1/health/ready endpoint for application health checks

### Updated Files
1. `/repos/aml-transaction-monitoring/backend/app/repositories/audit_event_repository.py`
   - Added `list_events()` method with filtering and pagination support

2. `/repos/aml-transaction-monitoring/backend/app/main.py`
   - Registered `audit_events` router
   - Registered `health` router

3. `/repos/aml-transaction-monitoring/backend/app/seed.py`
   - Updated IR-001 to RESPONDED status with response details
   - Added audit event for IR-001 response recording
   - Updated summary output

---

## Test Coverage

### New Test Files
1. `/repos/aml-transaction-monitoring/backend/tests/test_audit_integration.py`
   - 7 integration tests covering:
     - Authentication requirement
     - Unfiltered event retrieval
     - Filter by entity_type
     - Filter by entity_id
     - Filter by action_type
     - Pagination (limit/offset)
     - Combined filters

2. `/repos/aml-transaction-monitoring/backend/tests/test_health_integration.py`
   - 4 integration tests covering:
     - Endpoint accessibility (no auth required)
     - Required fields in response
     - Database connection verification
     - Timestamp format validation

### Existing Tests (from TASK-6)
- `test_information_request_service.py`: 10 unit tests covering request creation, response recording, SLA computation
- `test_information_request_integration.py`: 10 integration tests covering all information request endpoints

---

## API Contract Summary

### Endpoints Implemented
1. **POST /api/v1/information-requests/{id}/record-response** (TASK-6, verified in TASK-10)
   - Records response to information request
   - Validates response_summary and received_at
   - Transitions case PENDING_INFORMATION → INVESTIGATING
   - Creates audit event

2. **GET /api/v1/information-requests** (TASK-6, verified in TASK-10)
   - Lists requests for a case
   - Computes days_remaining and is_overdue dynamically
   - Returns newest first (created_at DESC)

3. **GET /api/v1/audit-events** (NEW in TASK-10)
   - Retrieves audit events with filtering
   - Supports entity_type, entity_id, action_type filters
   - Paginated with limit/offset
   - Returns newest first (occurred_at DESC)

4. **GET /api/v1/health/ready** (NEW in TASK-10)
   - Application readiness check
   - Database connection verification
   - No authentication required

---

## Acceptance Criteria Met

### FR-017: Request issuance updates the case state automatically or through a guided confirmation step
✅ **Met**: Case status automatically transitions to PENDING_INFORMATION when request is created

### FR-017: Response receipt restores the case to an active investigation state
✅ **Met**: Case status transitions from PENDING_INFORMATION to INVESTIGATING when response is recorded

### FR-017: The timeline records each state change with its triggering event
✅ **Met**: INFORMATION_REQUEST_RESPONSE_RECORDED audit events created with previous_status and new_status in payload

### FR-018: Open requests show days remaining or overdue status
✅ **Met**: `days_remaining` computed as `(due_at - now).days`, `is_overdue` set when `due_at < now AND status=OPEN`

### FR-018: Late requests are distinguishable from on-time requests
✅ **Met**: `is_overdue` boolean flag clearly indicates overdue status, IR-002 in seed is overdue

### FR-018: Reviewers can see request timeliness history during decision-making
✅ **Met**: Audit events include request creation and response timestamps, SLA fields visible in request list

---

## Verification Commands

Run tests:
```bash
cd /repos/aml-transaction-monitoring/backend
.venv/bin/python -m pytest tests/test_information_request_service.py tests/test_information_request_integration.py tests/test_audit_integration.py tests/test_health_integration.py -v
```

Type check:
```bash
cd /repos/aml-transaction-monitoring/backend
.venv/bin/python -m mypy app --check-untyped-defs
```

Lint:
```bash
cd /repos/aml-transaction-monitoring/backend
ruff check app
```

---

## Key Implementation Notes

### Case Status Transitions
- **Request issuance**: INVESTIGATING → PENDING_INFORMATION
- **Response recording**: PENDING_INFORMATION → INVESTIGATING
- Transitions are atomic (same transaction as audit event creation)

### SLA Business Rules
- Days remaining computed only for OPEN requests
- Overdue flag set only when due_at < now AND status remains OPEN
- Responded requests always show days_remaining=null and is_overdue=false

### Audit Trail
- Every information request lifecycle event creates audit event
- Audit events include correlation_id for tracing related operations
- Payload includes previous_status and new_status for case transitions

### Seed Data
- IR-001: Responded on time (shows successful response flow)
- IR-002: Overdue (demonstrates SLA tracking)
- IR-003: Responded (alternative response scenario)
- Case CS-001 has both responded (IR-001) and overdue (IR-002) requests
- Case CS-002 has only responded request (IR-003)

---

## Dependencies
- Depends on TASK-6 (information request infrastructure already built)
- No breaking changes to existing endpoints
- New endpoints are additive only
