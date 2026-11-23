# TASK-7 Backend Handoff: Evidence Gap Tracking and Information Request Creation

## API Endpoints

### POST /api/v1/cases/{caseId}/requests
Create a new information request for a case evidence gap.

**Request:**
```json
{
  "gap_id": "uuid",
  "target_party": "string",
  "delivery_channel": "string",
  "reason_text": "string",
  "due_at_utc": "ISO8601 datetime"
}
```

**Response (201):**
```json
{
  "request_id": "uuid",
  "request_ref": "IR-001",
  "case_id": "uuid",
  "gap_id": "uuid",
  "target_party": "string",
  "delivery_channel": "string",
  "reason_text": "string",
  "due_at_utc": "ISO8601 datetime",
  "status": "OPEN",
  "created_by_user_id": "uuid",
  "created_at_utc": "ISO8601 datetime"
}
```

**Headers:**
- `Authorization: Bearer <token>` (required)
- `X-Correlation-ID: <correlation-id>` (optional, generated if not provided)

**Behavior:**
- Creates information request with sequential reference (IR-001, IR-002, etc.)
- Transitions case status to PENDING_INFORMATION
- Sets case blocker_state to OPEN_REQUESTS
- Emits REQUEST_CREATED audit event
- Returns 404 if case not found
- Returns 401 if not authenticated

## Database Schema

### evidence_gaps
- `gap_id` UUID PRIMARY KEY
- `case_id` UUID NOT NULL REFERENCES aml_cases(case_id)
- `title` VARCHAR(255) NOT NULL
- `description` TEXT NOT NULL
- `status` VARCHAR(24) NOT NULL (OPEN, RESOLVED)
- `created_by_user_id` UUID NOT NULL REFERENCES users(user_id)
- `created_at_utc` TIMESTAMP NOT NULL
- `resolved_at_utc` TIMESTAMP NULL

### information_requests
- `request_id` UUID PRIMARY KEY
- `request_ref` VARCHAR(64) NOT NULL UNIQUE
- `case_id` UUID NOT NULL REFERENCES aml_cases(case_id)
- `gap_id` UUID NOT NULL REFERENCES evidence_gaps(gap_id)
- `target_party` VARCHAR(255) NOT NULL
- `delivery_channel` VARCHAR(64) NOT NULL
- `reason_text` TEXT NOT NULL
- `due_at_utc` TIMESTAMP NOT NULL
- `status` VARCHAR(24) NOT NULL (OPEN, OVERDUE, RESPONDED, RESOLVED)
- `created_by_user_id` UUID NOT NULL REFERENCES users(user_id)
- `response_summary` TEXT NULL
- `response_received_at_utc` TIMESTAMP NULL
- `created_at_utc` TIMESTAMP NOT NULL
- `updated_at_utc` TIMESTAMP NOT NULL

### request_attachments
- `request_attachment_id` UUID PRIMARY KEY
- `request_id` UUID NOT NULL REFERENCES information_requests(request_id)
- `attachment_ref` VARCHAR(64) NOT NULL UNIQUE
- `file_name` VARCHAR(255) NOT NULL
- `content_type` VARCHAR(128) NOT NULL
- `storage_path` VARCHAR(512) NOT NULL
- `uploaded_by_user_id` UUID NOT NULL REFERENCES users(user_id)
- `uploaded_at_utc` TIMESTAMP NOT NULL

## Seed Data

### Evidence Gaps
- `90000000-0000-0000-0000-000000000001` - CS-201, "Source of funds documentation", OPEN
- `90000000-0000-0000-0000-000000000002` - CS-202, "Beneficiary identity verification", OPEN
- `90000000-0000-0000-0000-000000000003` - CS-203, "Transaction purpose clarification", OPEN
- `90000000-0000-0000-0000-000000000004` - CS-203, "Previous transaction history", RESOLVED

### Information Requests
- `IR-001` (`a0000000-0000-0000-0000-000000000001`) - CS-201, OPEN, due date +3 days from now
- `IR-002` (`a0000000-0000-0000-0000-000000000002`) - CS-202, OVERDUE, due date -1 day from now
- `IR-003` (`a0000000-0000-0000-0000-000000000003`) - CS-203, OPEN, due date +1 day from now

Each request is linked to an evidence gap and has:
- Unique request reference (IR-XXX format)
- Target party (customer, compliance team, etc.)
- Delivery channel (Email, Phone, Internal system)
- Reason text explaining what information is needed
- Due date (some overdue, some future)
- Status (OPEN or OVERDUE)

## Workflow Flows

### Create Information Request Flow
1. Investigator identifies evidence gap in case
2. POST /api/v1/cases/{caseId}/requests with gap_id, target party, delivery channel, reason, and due date
3. Backend validates case exists
4. Backend generates sequential request reference (IR-001, IR-002, etc.)
5. Backend creates information_requests record with status OPEN
6. Backend updates case status to PENDING_INFORMATION
7. Backend sets case.current_blocker_state to OPEN_REQUESTS
8. Backend emits REQUEST_CREATED audit event with correlation_id
9. Backend returns 201 with created request details
10. Case now blocked from final decision until request resolved

### Blocker State Management
- When information request created with status OPEN: case blocker_state → OPEN_REQUESTS
- When request due_at_utc < now and status still OPEN: status → OVERDUE
- When all requests resolved: case blocker_state → NONE
- Frontend should display blocker warning banner when blocker_state != NONE
- Blocker state will be checked by future decision endpoint to prevent premature case closure

## Migration
- Migration `20261122_1400_006` creates evidence_gaps, information_requests, and request_attachments tables
- Includes foreign key constraints to aml_cases, evidence_gaps, and users
- Includes indexes on case_id and status for query performance
- Uses batch_alter_table for SQLite compatibility

## Models
- `EvidenceGap` - ORM model for evidence_gaps table
- `InformationRequest` - ORM model for information_requests table with relationships to case, gap, and attachments
- `RequestAttachment` - ORM model for request_attachments table
- Added relationships to AmlCase model for evidence_gaps and information_requests

## Testing
- `test_information_request_service.py::test_create_request` - Verifies request creation, case status transition, and audit event
- `test_information_request_service.py::test_create_request_case_not_found` - Verifies error handling for non-existent case

## Frontend Integration Notes
- Screen 3 (Case Investigation) displays evidence gaps from workspace endpoint
- Screen 4 (Resolve Information Request) will use this endpoint to create requests
- Request creation transitions case to PENDING_INFORMATION which affects workflow progression
- Blocker state prevents moving to readiness review until requests resolved
- Timeline on Screen 3 shows REQUEST_CREATED audit events
