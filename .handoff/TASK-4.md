# TASK-4 Handoff: Backend Feature B2 - Case Creation and Overview

## Implemented Endpoints

### POST /api/v1/alerts/{alert_id}/cases
**Purpose**: Create a case from an alert with transactional integrity

**Request Body**:
```json
{
  "case_priority": "HIGH",
  "initial_rationale": "Large cross-border transfer with high risk score requiring investigation"
}
```

**Response** (200):
```json
{
  "case_id": "case-CS-003",
  "case_number": "CS-003",
  "source_alert_id": "alert-001",
  "status": "INVESTIGATING",
  "created_at": "2026-11-21T10:30:00Z"
}
```

**Behavior**:
- Creates case with status=INVESTIGATING, assigned to actor
- Creates case_alert_link preserving alert identifier and risk context
- Updates alert status to ESCALATED_TO_CASE
- Creates CASE_CREATED audit event
- Creates ALERT_LINKED_TO_CASE audit event
- All operations in single transaction

**Error Responses**:
- 404: Alert not found
- 401: Unauthorized

### GET /api/v1/cases/{case_id}
**Purpose**: Get consolidated case overview with aggregated counts and recent activity

**Response** (200):
```json
{
  "case_id": "case-CS-001",
  "case_number": "CS-001",
  "status": "INVESTIGATING",
  "priority": "CRITICAL",
  "assigned_user_id": "usr-001",
  "assigned_user_name": "Riya Sharma",
  "recommendation_state": "DRAFT",
  "recommendation_outcome": null,
  "flagged_value_total": 285000.00,
  "currency": "USD",
  "linked_alert_count": 1,
  "open_information_request_count": 0,
  "overdue_information_request_count": 0,
  "recent_activity": [
    {
      "event_id": "audit-001",
      "event_type": "CASE_CREATED",
      "occurred_at": "2026-11-21T10:00:00Z",
      "actor_display": "Riya Sharma",
      "summary": "Case created from alert"
    }
  ],
  "created_at": "2026-11-21T10:00:00Z",
  "updated_at": "2026-11-21T10:00:00Z"
}
```

**Aggregations**:
- `linked_alert_count`: Count of alerts linked via case_alert_links
- `flagged_value_total`: Sum of transaction amounts from linked alerts
- `open_information_request_count`: Count of information_requests with status=OPEN
- `overdue_information_request_count`: Count of OPEN requests with due_at < now
- `recent_activity`: Last 10 audit events for this case with formatted summaries

**Error Responses**:
- 404: Case not found
- 401: Unauthorized

## Seed Data

The seed script creates 2 sample cases:

### Case CS-001
- **Case ID**: case-CS-001
- **Source Alert**: alert-001
- **Customer**: cust-001 (Acme Global Trading Ltd)
- **Priority**: CRITICAL
- **Status**: INVESTIGATING
- **Assigned To**: usr-001 (Riya Sharma, investigator)
- **Flagged Value**: $285,000.00
- **Created By**: usr-001

### Case CS-002
- **Case ID**: case-CS-002
- **Source Alert**: alert-008
- **Customer**: cust-002 (Brighton Investment Partners)
- **Priority**: HIGH
- **Status**: INVESTIGATING
- **Assigned To**: usr-001 (Riya Sharma, investigator)
- **Flagged Value**: $125,000.00
- **Created By**: usr-001

## Key Implementation Details

### Case Creation Flow
1. Service validates alert exists
2. Service validates actor exists
3. Service generates sequential case number (CS-XXX format)
4. Repository creates case with status=INVESTIGATING
5. Repository creates case_alert_link
6. Repository updates alert.status to ESCALATED_TO_CASE
7. Service creates CASE_CREATED audit event
8. Service creates ALERT_LINKED_TO_CASE audit event
9. Transaction commits all changes atomically

### Case Overview Assembly
1. Repository retrieves case by ID
2. Repository resolves assigned_user_name if assigned
3. Repository counts linked alerts via case_alert_links join
4. Repository sums transaction amounts from linked alerts via transaction join
5. Repository counts open information_requests (status=OPEN)
6. Repository counts overdue requests (status=OPEN AND due_at < now)
7. Repository retrieves last 10 audit_events for case
8. Service formats audit events into human-readable summaries
9. Service returns complete CaseOverviewResponse

### Database Tables Used
- **aml_cases**: Core case record
- **case_alert_links**: Alert-to-case linkage
- **alerts**: Source alert and status update
- **information_requests**: Request counts for overview
- **audit_events**: Activity timeline
- **users**: Actor and assignee resolution
- **transactions**: Flagged value aggregation

## Testing

### Unit Tests (test_case_service.py)
- ✓ Create case from alert success
- ✓ Create case fails when alert not found
- ✓ Get case overview success with aggregations
- ✓ Get case overview fails when case not found
- ✓ Case overview correctly counts open/overdue requests

### Integration Tests (test_case_integration.py)
- ✓ Create case from alert endpoint success
- ✓ Create case fails for nonexistent alert (404)
- ✓ Create case requires authentication (401)
- ✓ Get case overview endpoint success
- ✓ Get case overview returns 404 for nonexistent case
- ✓ Get case overview requires authentication (401)

## Acceptance Criteria Coverage

### FR-003: Case creation from alert
- ✅ Preserves original alert identifier (via case_alert_links.alert_id)
- ✅ Preserves risk context (via case_alert_links.selection_basis = initial_rationale)
- ✅ Resulting case shows linked alert (linked_alert_count in overview)
- ✅ Triage action stores auditable rationale (ALERT_LINKED_TO_CASE audit event with payload)

### FR-006: Case overview
- ✅ Shows case metadata (status, priority, assignment, recommendation_state)
- ✅ Shows linked alert count (aggregated from case_alert_links)
- ✅ Aggregated flagged value calculated from linked alert transactions
- ✅ Recent activity includes notes, assignment changes, workflow events (from audit_events)

## Files Modified/Created

### Created
- `/repos/aml-transaction-monitoring/backend/app/schemas/case_schemas.py`
- `/repos/aml-transaction-monitoring/backend/app/repositories/case_repository.py`
- `/repos/aml-transaction-monitoring/backend/app/services/case_service.py`
- `/repos/aml-transaction-monitoring/backend/app/routers/cases.py`
- `/repos/aml-transaction-monitoring/backend/tests/test_case_service.py`
- `/repos/aml-transaction-monitoring/backend/tests/test_case_integration.py`
- `/repos/aml-transaction-monitoring/.handoff/TASK-4.md`

### Modified
- `/repos/aml-transaction-monitoring/backend/app/routers/alerts.py` - Added POST /api/v1/alerts/{alert_id}/cases endpoint
- `/repos/aml-transaction-monitoring/backend/app/main.py` - Registered cases router
- `/repos/aml-transaction-monitoring/backend/app/seed.py` - Added 2 sample cases, case_alert_links, and audit events

## Next Steps

The following features remain for full case workspace implementation:
- TASK-5: Case notes (FR-007)
- TASK-6: Case status transitions (FR-008)
- TASK-7: Investigation recommendation submission (FR-010)
- TASK-8: Customer and transaction evidence retrieval (FR-011, FR-012, FR-013, FR-015)
- TASK-9: Information request issuance and tracking (FR-016, FR-017, FR-018)
- TASK-10: Review handoff package (FR-021)
