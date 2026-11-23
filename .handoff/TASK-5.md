# TASK-5: Backend Feature B3 - Historical Rule Snapshots and Linked Alerts

## Overview

This task implements immutable historical rule evaluation snapshots and the API endpoint for linking additional alerts to existing cases. It completes FR-004 (Historical Rule Snapshots) and FR-006 (Multi-Alert Linkage).

## Implemented Features

### 1. Rule Evaluation Snapshots

**Model:** `app/models/rule_snapshot.py`

- Immutable historical rule evaluation records
- Captures exact rule state at alert evaluation time
- Never recalculated or modified after creation

**Schema:**
```python
RuleEvaluationSnapshot:
  - snapshot_id: UUID (PK)
  - alert_id: UUID (FK → alerts)
  - rule_code: VARCHAR(64)
  - rule_name: VARCHAR(255)
  - rule_version: VARCHAR(32)  # Preserved verbatim (e.g., "v3.2")
  - outcome: VARCHAR(16)  # MATCH | PASS
  - condition_text: TEXT
  - evaluated_from_utc: TIMESTAMP
  - evaluated_to_utc: TIMESTAMP
  - immutable_hash: VARCHAR(128)
  - created_at_utc: TIMESTAMP
```

**Repository:** `app/repositories/rule_snapshot_repository.py`

- `list_for_alert(alert_id)` - Returns snapshots ordered by outcome (MATCH first), then rule_name

### 2. Extended Evidence Response

**Schemas:** `app/schemas/evidence_schemas.py`

- `RuleSnapshotItem` - Individual rule snapshot DTO
- `AlertEvidenceResponse` - Now includes `rule_snapshots: list[RuleSnapshotItem]`

**Service:** `app/services/evidence_service.py`

- Extended to retrieve and include rule snapshots for each alert
- Snapshots returned in consistent order (MATCH outcomes first)

### 3. Link Additional Alerts Endpoint

**Route:** `POST /api/v1/cases/{caseId}/alerts`

**Request Body:**
```json
{
  "alert_id": "uuid"
}
```

**Response (201 Created):**
```json
{
  "case_alert_link_id": "uuid",
  "case_id": "uuid",
  "alert_id": "uuid",
  "is_primary": false,
  "linked_at_utc": "2026-11-22T14:30:00Z"
}
```

**Behavior:**
- Creates case_alert_link with `is_primary=False`
- Emits `ALERT_LINKED` audit event
- Returns 404 if case or alert not found
- Returns 409 if alert already linked to case
- Requires authentication via Bearer token
- Requires `X-Correlation-ID` header

**Implementation:** `app/routers/cases.py`

### 4. Database Migration

**Migration:** `alembic/versions/20261122_1400_004_create_rule_snapshots_table.py`

- Creates `rule_evaluation_snapshots` table
- Creates index on `alert_id` for efficient lookup
- Uses batch operations for SQLite compatibility

### 5. Seed Data

**Updated:** `app/seed.py`

- Added `seed_rule_snapshots()` function
- Creates 3-5 rule snapshots per alert with varied:
  - Rule names (High Value Transaction, PEP Detection, Cross-Border, etc.)
  - Versions (v2.1, v2.3, v2.5, v3.2, v4.0)
  - Outcomes (MATCH, PASS)
  - Condition text
- Added secondary alert links to cases:
  - CS-201: Primary ALT-001, Secondary ALT-006
  - CS-202: Primary ALT-002, Secondary ALT-005
  - CS-203: Primary ALT-003, Secondary ALT-008
- Each case now has 2 linked alerts (1 primary, 1 secondary)

## API Endpoints

### GET /api/v1/alerts/{alertId}/evidence

**Changes:**
- Now includes `rule_snapshots` array in response
- Each snapshot includes rule_code, rule_name, rule_version, outcome, condition_text

**Example Response:**
```json
{
  "alert_id": "40000000-0000-0000-0000-000000000001",
  "alert_ref": "ALT-2026-001",
  "priority": "Critical",
  "risk_score": 95,
  "status": "New",
  "triggered_at_utc": "2026-11-22T12:00:00Z",
  "transaction": { ... },
  "customer": { ... },
  "account": { ... },
  "rule_snapshots": [
    {
      "snapshot_id": "70000000-0000-0000-0000-000000000001",
      "rule_code": "AML-HIGH-VALUE-001",
      "rule_name": "High Value Transaction to Offshore Jurisdiction",
      "rule_version": "v3.2",
      "outcome": "MATCH",
      "condition_text": "Transaction amount >= $50,000 AND destination in [VG, KY, PA, BM]",
      "evaluated_from_utc": "2026-11-22T11:00:00Z",
      "evaluated_to_utc": "2026-11-22T12:00:00Z"
    },
    {
      "snapshot_id": "70000000-0000-0000-0000-000000000002",
      "rule_code": "AML-RAPID-MOVEMENT-001",
      "rule_name": "Rapid Movement of Funds",
      "rule_version": "v2.1",
      "outcome": "PASS",
      "condition_text": "Transaction count in 24h window > 5 with total > $100,000",
      "evaluated_from_utc": "2026-11-22T11:00:00Z",
      "evaluated_to_utc": "2026-11-22T12:00:00Z"
    }
  ]
}
```

### POST /api/v1/cases/{caseId}/alerts

**New endpoint** for linking additional alerts to existing cases.

**Request:**
```bash
POST /api/v1/cases/50000000-0000-0000-0000-000000000001/alerts
Authorization: Bearer <token>
X-Correlation-ID: corr-12345
Content-Type: application/json

{
  "alert_id": "40000000-0000-0000-0000-000000000006"
}
```

**Response:**
```json
{
  "case_alert_link_id": "60000000-0000-0000-0000-000000000004",
  "case_id": "50000000-0000-0000-0000-000000000001",
  "alert_id": "40000000-0000-0000-0000-000000000006",
  "is_primary": false,
  "linked_at_utc": "2026-11-22T14:30:00.123456Z"
}
```

## Seed Data IDs

### Rule Snapshot Examples

Alert ALT-2026-001 (40000000-0000-0000-0000-000000000001):
- 70000000-0000-0000-0000-000000000001 - High Value (v3.2, MATCH)
- 70000000-0000-0000-0000-000000000002 - Rapid Movement (v2.1, PASS)
- 70000000-0000-0000-0000-000000000003 - Structuring (v4.0, PASS)

Alert ALT-2026-002 (40000000-0000-0000-0000-000000000002):
- 70000000-0000-0000-0000-000000000004 - PEP Offshore (v3.2, MATCH)
- 70000000-0000-0000-0000-000000000005 - High Value (v3.2, MATCH)
- 70000000-0000-0000-0000-000000000006 - Unusual Currency (v2.5, PASS)
- 70000000-0000-0000-0000-000000000007 - Velocity Spike (v1.8, PASS)

### Cases with Linked Alerts

**CS-201** (50000000-0000-0000-0000-000000000001):
- Primary: ALT-2026-001 (40000000-0000-0000-0000-000000000001)
- Secondary: ALT-2026-006 (40000000-0000-0000-0000-000000000006)

**CS-202** (50000000-0000-0000-0000-000000000002):
- Primary: ALT-2026-002 (40000000-0000-0000-0000-000000000002)
- Secondary: ALT-2026-005 (40000000-0000-0000-0000-000000000005)

**CS-203** (50000000-0000-0000-0000-000000000003):
- Primary: ALT-2026-003 (40000000-0000-0000-0000-000000000003)
- Secondary: ALT-2026-008 (40000000-0000-0000-0000-000000000008)

## Example Flows

### View Alert Evidence with Rule Snapshots

```bash
curl -X GET http://localhost:8000/api/v1/alerts/40000000-0000-0000-0000-000000000001/evidence \
  -H "Authorization: Bearer <token>"
```

Returns alert with transaction, customer, account, and 3 rule snapshots (1 MATCH, 2 PASS).

### Link Additional Alert to Case

```bash
curl -X POST http://localhost:8000/api/v1/cases/50000000-0000-0000-0000-000000000001/alerts \
  -H "Authorization: Bearer <token>" \
  -H "X-Correlation-ID: corr-abc123" \
  -H "Content-Type: application/json" \
  -d '{"alert_id": "40000000-0000-0000-0000-000000000004"}'
```

Creates secondary alert link and emits audit event.

## Testing

### Test Files

- `tests/test_rule_snapshot_service.py` - Rule snapshot repository tests
- `tests/test_case_service.py::test_add_alert_link` - Secondary alert link test

### Run Tests

```bash
cd /repos/aml-transaction-monitoring/backend
.venv/bin/python -m pytest tests/test_rule_snapshot_service.py -v
.venv/bin/python -m pytest tests/test_case_service.py::test_add_alert_link -v
```

## Compliance & Requirements

**FR-004 (Historical Rule Snapshots):**
- ✅ System displays each relevant rule name, version, and outcome
- ✅ MATCH and PASS outcomes displayed distinctly
- ✅ Explanatory condition text for each rule evaluation
- ✅ Changes to rule definitions do not alter historical snapshots
- ✅ Backend persists immutable rule-evaluation artifacts

**FR-006 (Multi-Alert Linkage):**
- ✅ System allows one or more alerts to be linked to existing case
- ✅ Case workspace shows linked alert references
- ✅ Every alert-to-case linkage recorded in audit trail
- ✅ Interface distinguishes primary alert from subsequently linked alerts (is_primary flag)

## Notes

- Rule versions preserved exactly as stored (e.g., "v3.2", "v2.1")
- Snapshots ordered by outcome (MATCH first) then by rule name
- `immutable_hash` computed from alert_id, rule_code, outcome, and timestamp
- All timestamps in UTC
- Secondary links always have `is_primary=False`
- Audit events use same correlation_id as request for traceability
