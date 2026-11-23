# TASK-4 Handoff: Transaction Evidence and Case Creation

## Completed Endpoints

### GET /api/v1/alerts/{alertId}/evidence
Retrieves full alert evidence read model with nested transaction, customer, and account context.

**Response Shape:**
```json
{
  "alert_id": "uuid",
  "alert_ref": "string",
  "priority": "string",
  "risk_score": "integer",
  "status": "string",
  "triggered_at_utc": "datetime",
  "transaction": {
    "transaction_id": "uuid",
    "transaction_ref": "string",
    "amount": "decimal",
    "currency_code": "string",
    "source_country_code": "string",
    "destination_country_code": "string",
    "executed_at_utc": "datetime"
  },
  "customer": {
    "customer_id": "uuid",
    "customer_name": "string",
    "pep_flag": "boolean",
    "country_code": "string"
  },
  "account": {
    "account_id": "uuid",
    "account_ref": "string",
    "account_type": "string"
  }
}
```

**Example:**
- Alert ID: `40000000-0000-0000-0000-000000000001` (ALT-2026-001)
- Returns nested transaction, customer (Acme Corp), and account details

### POST /api/v1/cases
Creates a new case from a primary alert. Links the alert as the primary alert and emits audit events.

**Request:**
```json
{
  "alert_id": "uuid"
}
```

**Response:**
```json
{
  "case_id": "uuid",
  "case_ref": "string",
  "primary_alert_id": "uuid",
  "created_by_user_id": "uuid",
  "status": "string",
  "created_at_utc": "datetime"
}
```

**Case Reference Generation:**
Case references are sequential: CS-1, CS-2, CS-3, etc.

**Audit Events Emitted:**
1. `CASE_CREATED` - Records case creation with case_ref, primary_alert_id, status
2. `ALERT_LINKED` - Records alert linkage with case_id, alert_id, is_primary=true

**Example:**
- POST with alert_id: `40000000-0000-0000-0000-000000000001`
- Creates case with ref: `CS-204` (sequential number depends on existing cases)
- Status: `OPEN`
- Creates primary case_alert_link with is_primary=true

## Seed Data

**Sample Cases:**
- CS-201: `50000000-0000-0000-0000-000000000001` (OPEN, created from ALT-2026-001)
- CS-202: `50000000-0000-0000-0000-000000000002` (INVESTIGATING, created from ALT-2026-002)
- CS-203: `50000000-0000-0000-0000-000000000003` (PENDING_INFORMATION, created from ALT-2026-003)

**Sample Alerts with Transaction Data:**
- ALT-2026-001: `40000000-0000-0000-0000-000000000001` (Critical, $45,000 USD, US→AE, Acme Corp)
- ALT-2026-002: `40000000-0000-0000-0000-000000000002` (Critical, $38,000 EUR, FR→RU, Beta Industries)
- ALT-2026-003: `40000000-0000-0000-0000-000000000003` (High, $22,000 GBP, GB→CN, Gamma Ltd)
- ALT-2026-004: `40000000-0000-0000-0000-000000000004` (High, $88,000 USD, US→KP, Delta Logistics)

**Users:**
- Investigator: investigator@example.com / investigator123 (`00000000-0000-0000-0000-000000000001`)
- Officer: officer@example.com / officer123 (`00000000-0000-0000-0000-000000000002`)

## Database Schema

**aml_cases:**
- case_id (UUID, PK)
- case_ref (VARCHAR(64), UNIQUE)
- primary_alert_id (UUID, FK → alerts.alert_id)
- created_by_user_id (UUID, FK → users.user_id)
- assigned_officer_user_id (UUID, FK → users.user_id, nullable)
- status (VARCHAR(40), CHECK constraint)
- current_blocker_state (VARCHAR(24), default 'NONE')
- created_at_utc, updated_at_utc (TIMESTAMP)

**case_alert_links:**
- case_alert_link_id (UUID, PK)
- case_id (UUID, FK → aml_cases.case_id)
- alert_id (UUID, FK → alerts.alert_id)
- is_primary (BOOLEAN, default false)
- linked_by_user_id (UUID, FK → users.user_id)
- linked_at_utc (TIMESTAMP)
- UNIQUE(case_id, alert_id)

## Flows

**Evidence Review Flow:**
1. User views alert queue (GET /api/v1/alerts)
2. User selects alert and navigates to evidence (GET /api/v1/alerts/{alertId}/evidence)
3. Backend joins alert, transaction, customer, and account tables
4. Returns nested response preserving full context

**Case Creation Flow:**
1. User views alert evidence screen
2. User clicks "Create Case"
3. Frontend POST /api/v1/cases with alert_id
4. Backend generates next case_ref (e.g., CS-204)
5. Backend creates AmlCase record
6. Backend creates CaseAlertLink with is_primary=true
7. Backend emits CASE_CREATED and ALERT_LINKED audit events
8. Backend commits transaction and returns case details
9. Frontend navigates to case investigation screen with new case_id

## Technical Notes

- Evidence service uses SQLAlchemy joins to assemble nested read model in single query
- Case service uses transaction to ensure case, link, and audit events are atomic
- Case reference generation queries existing cases to get next sequential number
- Audit events capture actor, role, correlation_id, and details_json for traceability
- All UUID fields use sqlalchemy.Uuid type for consistent storage
- All timestamps are UTC with explicit timezone handling
