# TASK-3 Backend Alert API Handoff

## Implemented Endpoints

### GET /api/v1/alerts
Retrieve paginated alert queue with prioritization, filtering, and search.

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `priority` (optional): Filter by priority - `Critical`, `High`, `Medium`, or `Low`
- `ownership` (optional): Filter by ownership - `All`, `Unassigned`, or `Assigned to Me`
- `status` (optional): Filter by status - `New`, `Under Review`, `Escalated`, or `Resolved`
- `search` (optional): Search by alert ID or customer name (case-insensitive partial match)
- `page` (optional, default=1): Page number (1-indexed)
- `page_size` (optional, default=20, max=100): Items per page

**Response:** 200 OK
```json
{
  "items": [
    {
      "alert_id": "40000000-0000-0000-0000-000000000001",
      "alert_ref": "ALT-2026-001",
      "priority": "Critical",
      "risk_score": 95,
      "status": "New",
      "owner_user_id": null,
      "triggered_at_utc": "2026-11-22T12:00:00Z",
      "transaction_amount": "95000.00",
      "transaction_currency_code": "USD",
      "source_country_code": "GB",
      "destination_country_code": "VG",
      "customer_id": "10000000-0000-0000-0000-000000000001",
      "customer_name": "John Smith"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

**Default Ordering:** `risk_score DESC`, then `triggered_at_utc DESC`

### POST /api/v1/alerts/{alertId}/assign
Assign alert to current authenticated user.

**Authentication:** Required (Bearer token)

**Headers:**
- `X-Correlation-ID` (required): Correlation ID for audit trail

**Request Body:** Empty (user inferred from auth token)

**Response:** 200 OK
```json
{
  "alert_id": "40000000-0000-0000-0000-000000000001",
  "owner_user_id": "00000000-0000-0000-0000-000000000001",
  "assigned_at_utc": "2026-11-22T14:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Alert not found with given ID
- `409 Conflict`: Alert already assigned to a different user

**Idempotency:** Assigning an alert already assigned to the same user succeeds and returns existing assignment.

**Audit Event:** Creates audit event with `entity_type="alert"`, `action_type="ALERT_ASSIGNED"`, actor details, and correlation ID.

## Seed Data

### Default User Credentials
```
Investigator 1: investigator@example.com / investigator123
               UUID: 00000000-0000-0000-0000-000000000001

Investigator 2: investigator2@example.com / investigator123
               UUID: 00000000-0000-0000-0000-000000000005

Officer:       officer@example.com / officer123
               UUID: 00000000-0000-0000-0000-000000000002

Auditor:       auditor@example.com / auditor123
               UUID: 00000000-0000-0000-0000-000000000003

Supervisor:    supervisor@example.com / supervisor123
               UUID: 00000000-0000-0000-0000-000000000004
```

### Sample Alert IDs and States

**Unassigned Critical Alerts:**
- `ALT-2026-001` (Risk: 95, Priority: Critical, Status: New)
  - Alert ID: `40000000-0000-0000-0000-000000000001`
  - Customer: John Smith (GB → VG, $95,000)

**Assigned Critical Alerts:**
- `ALT-2026-002` (Risk: 92, Priority: Critical, Status: Under Review, Owner: Investigator 1)
  - Alert ID: `40000000-0000-0000-0000-000000000002`
  - Customer: Maria Garcia (ES → PA, €150,000)

- `ALT-2026-010` (Risk: 90, Priority: Critical, Status: Under Review, Owner: Investigator 1)
  - Alert ID: `40000000-0000-0000-0000-000000000010`
  - Customer: Svetlana Ivanova (RU → MT, $125,000)

**Unassigned High Priority Alerts:**
- `ALT-2026-004` (Risk: 88, Priority: High, Status: New)
  - Alert ID: `40000000-0000-0000-0000-000000000004`
  - Customer: Ahmed Hassan (EG → CH, $180,000)

- `ALT-2026-008` (Risk: 85, Priority: High, Status: New)
  - Alert ID: `40000000-0000-0000-0000-000000000008`
  - Customer: Zhang Wei (CN → HK, $88,000)

**Assigned High Priority Alert:**
- `ALT-2026-005` (Risk: 82, Priority: High, Status: Under Review, Owner: Investigator 2)
  - Alert ID: `40000000-0000-0000-0000-000000000005`
  - Customer: Svetlana Ivanova (RU → CY, $65,000)

**Unassigned Medium Priority Alerts:**
- `ALT-2026-003` (Risk: 65, Priority: Medium, Status: New)
  - Alert ID: `40000000-0000-0000-0000-000000000003`
  - Customer: Zhang Wei (CN → US, $25,000)

- `ALT-2026-006` (Risk: 70, Priority: Medium, Status: New)
  - Alert ID: `40000000-0000-0000-0000-000000000006`
  - Customer: John Smith (GB → KY, £45,000)

**Escalated Medium Priority Alert:**
- `ALT-2026-009` (Risk: 68, Priority: Medium, Status: Escalated, Owner: Investigator 2)
  - Alert ID: `40000000-0000-0000-0000-000000000009`
  - Customer: Ahmed Hassan (EG → AE, $52,000)

**Resolved Low Priority Alert:**
- `ALT-2026-007` (Risk: 50, Priority: Low, Status: Resolved, Owner: Investigator 1)
  - Alert ID: `40000000-0000-0000-0000-000000000007`
  - Customer: Maria Garcia (ES → FR, €12,000)

## Testing Scenarios

### Queue Retrieval
1. **Default Queue (Highest Priority First)**
   ```
   GET /api/v1/alerts
   Authorization: Bearer <token>
   ```
   Expected: Alerts ordered by risk_score DESC, ALT-2026-001 (95) appears first

2. **Filter by Critical Priority**
   ```
   GET /api/v1/alerts?priority=Critical
   Authorization: Bearer <token>
   ```
   Expected: Only ALT-2026-001, ALT-2026-002, ALT-2026-010 returned

3. **Filter by Unassigned**
   ```
   GET /api/v1/alerts?ownership=Unassigned
   Authorization: Bearer <token>
   ```
   Expected: Only unassigned alerts (owner_user_id is null)

4. **Filter by Assigned to Me** (logged in as investigator@example.com)
   ```
   GET /api/v1/alerts?ownership=Assigned%20to%20Me
   Authorization: Bearer <investigator1_token>
   ```
   Expected: ALT-2026-002, ALT-2026-007, ALT-2026-010

5. **Search by Customer Name**
   ```
   GET /api/v1/alerts?search=Garcia
   Authorization: Bearer <token>
   ```
   Expected: ALT-2026-002, ALT-2026-007 (both belong to Maria Garcia)

6. **Search by Alert ID**
   ```
   GET /api/v1/alerts?search=ALT-2026-004
   Authorization: Bearer <token>
   ```
   Expected: Only ALT-2026-004 returned

7. **Pagination**
   ```
   GET /api/v1/alerts?page=1&page_size=5
   Authorization: Bearer <token>
   ```
   Expected: First 5 alerts, total=10, page=1, page_size=5

### Alert Assignment
1. **Assign Unassigned Alert** (ALT-2026-001)
   ```
   POST /api/v1/alerts/40000000-0000-0000-0000-000000000001/assign
   Authorization: Bearer <investigator1_token>
   X-Correlation-ID: correlation-123
   ```
   Expected: 200 OK with assignment details, audit event created

2. **Idempotent Assignment** (assign same alert to same user again)
   ```
   POST /api/v1/alerts/40000000-0000-0000-0000-000000000001/assign
   Authorization: Bearer <investigator1_token>
   X-Correlation-ID: correlation-124
   ```
   Expected: 200 OK with existing assignment (no error)

3. **Conflicting Assignment** (try to assign ALT-2026-002 already assigned to Investigator 1)
   ```
   POST /api/v1/alerts/40000000-0000-0000-0000-000000000002/assign
   Authorization: Bearer <investigator2_token>
   X-Correlation-ID: correlation-125
   ```
   Expected: 409 Conflict with error detail

4. **Missing Correlation ID**
   ```
   POST /api/v1/alerts/40000000-0000-0000-0000-000000000001/assign
   Authorization: Bearer <investigator1_token>
   (no X-Correlation-ID header)
   ```
   Expected: 422 Unprocessable Entity (missing required header)

5. **Non-existent Alert**
   ```
   POST /api/v1/alerts/99999999-9999-9999-9999-999999999999/assign
   Authorization: Bearer <investigator1_token>
   X-Correlation-ID: correlation-126
   ```
   Expected: 404 Not Found

## Database Schema Changes

### New Tables Created (Migration 002)

- `customers`: Customer master data with PEP flag and country code
- `accounts`: Account records linked to customers
- `transactions`: Transaction records with amount, currency, corridor
- `alerts`: Alert records with priority, risk score, status, ownership
- `audit_events`: Immutable audit trail for all workflow actions

### Foreign Key Relationships

- `accounts.customer_id` → `customers.customer_id`
- `transactions.account_id` → `accounts.account_id`
- `alerts.transaction_id` → `transactions.transaction_id`
- `alerts.customer_id` → `customers.customer_id`
- `alerts.owner_user_id` → `users.user_id` (nullable)
- `audit_events.actor_user_id` → `users.user_id`

### Indexes Created

- `alerts.alert_ref` (unique)
- `alerts.priority`
- `alerts.risk_score`
- `alerts.status`
- `accounts.account_ref` (unique)
- `transactions.transaction_ref` (unique)
- `audit_events.entity_type`
- `audit_events.entity_id`
- `audit_events.correlation_id`
- `audit_events.occurred_at_utc`

## Running Migrations and Seed

```bash
cd /repos/aml-transaction-monitoring/backend
alembic upgrade head
python app/seed.py
```

## API Base URL

All endpoints are mounted under the `/api/v1` prefix.

Full paths:
- `GET /api/v1/alerts`
- `POST /api/v1/alerts/{alertId}/assign`
