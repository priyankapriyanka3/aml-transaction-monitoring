# TASK-3 Handoff: Backend Feature B1 - Alert Queue and Assignment

## Implemented Endpoints

All endpoints mounted under `/api/v1`:

### Authentication Endpoints

#### POST /api/v1/auth/login
**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "auth_token": "string (JWT)",
  "token_type": "Bearer",
  "session_id": "string (UUID)",
  "user": {
    "user_id": "string",
    "username": "string",
    "display_name": "string",
    "roles": ["string"],
    "primary_role": "string"
  }
}
```

**Error Responses:**
- 401: Invalid credentials
- 422: Validation error

#### POST /api/v1/auth/logout
**Request:**
```json
{
  "session_id": "string"
}
```

**Response (200):**
```json
{
  "detail": "Session revoked successfully",
  "session_id": "string"
}
```

**Error Responses:**
- 404: Session not found

### Alert Endpoints

#### GET /api/v1/alerts
**Query Parameters:**
- `status`: Filter by status (optional)
- `priority`: Filter by priority (optional)
- `assignee_id`: Filter by assignee user ID or "UNASSIGNED" (optional)
- `risk_score_min`: Minimum risk score 0-100 (optional)
- `risk_score_max`: Maximum risk score 0-100 (optional)
- `generation`: Filter by generation source (optional)
- `search`: Search across alert/customer/transaction IDs (optional)
- `sort_by`: Sort field - priority, risk_score, created_at, status (default: priority)
- `sort_direction`: Sort direction - asc or desc (default: desc)
- `limit`: Page size 1-100 (default: 20)
- `offset`: Offset for pagination (default: 0)

**Headers:**
- `Authorization: Bearer <auth_token>`

**Response (200):**
```json
{
  "items": [
    {
      "alert_id": "string",
      "transaction_id": "string",
      "customer_id": "string",
      "status": "string",
      "priority": "string",
      "risk_score": 0-100,
      "matched_rule_codes_json": "string (JSON)",
      "generation": "string",
      "assigned_user_id": "string | null",
      "triage_outcome": "string | null",
      "triage_rationale": "string | null",
      "triaged_by_user_id": "string | null",
      "triaged_at": "datetime | null",
      "created_at": "datetime",
      "updated_at": "datetime",
      "customer_name": "string | null",
      "transaction_amount": "number | null",
      "transaction_currency": "string | null",
      "assigned_user_name": "string | null"
    }
  ],
  "total_count": 0,
  "limit": 20,
  "offset": 0
}
```

**Error Responses:**
- 401: Invalid or expired authentication token

#### POST /api/v1/alerts/{alert_id}/claim
**Path Parameters:**
- `alert_id`: Alert ID to claim

**Headers:**
- `Authorization: Bearer <auth_token>`

**Request:**
```json
{
  "assignee_user_id": "string",
  "assignment_reason": "string | null"
}
```

**Response (200):**
```json
{
  "alert_id": "string",
  "status": "string",
  "assigned_user_id": "string",
  "assigned_user_name": "string",
  "assigned_at": "datetime",
  "assigned_by_user_id": "string"
}
```

**Error Responses:**
- 401: Invalid or expired authentication token
- 404: Alert not found or assignee user not found

## Seed Data

### User Credentials
The seed creates two users with the following credentials:

**Investigator:**
- Username: `riya`
- Password: `password123`
- Role: investigator
- Display Name: Riya Sharma

**Officer:**
- Username: `morgan`
- Password: `password123`
- Role: officer
- Display Name: Morgan Chen

### Sample Data Created
- **Users:** 2 (investigator and officer)
- **Customers:** 3 (Acme Global Trading Ltd, Brighton Investment Partners, Clearwater Holdings Inc)
- **Accounts:** 3 (one per customer)
- **Transactions:** 5 (ranging from $45k CAD to $450k USD)
- **Detection Rule Snapshots:** 2 (RULE-001 v3.2, RULE-002 v2.1)
- **Alerts:** 10 with varying:
  - Statuses: NEW, UNDER_REVIEW, ESCALATED_TO_CASE, CLOSED_NON_ACTIONABLE
  - Priorities: CRITICAL, HIGH, MEDIUM, LOW
  - Risk Scores: 38-95
  - Assignments: Some assigned to riya, some to morgan, some unassigned

### Sample Alert IDs
- `alert-001` through `alert-010`

## Authentication Flow

1. **Login:** POST /api/v1/auth/login with username/password
2. **Receive:** JWT token in `auth_token` field and `session_id`
3. **Use:** Include JWT in Authorization header: `Bearer <auth_token>`
4. **Logout:** POST /api/v1/auth/logout with `session_id` to revoke session

## Security Features

- Passwords hashed with bcrypt cost factor 12
- JWT tokens include exp claim
- Session-based token revocation
- Token hash stored in session_records (SHA-256)
- All protected endpoints require valid JWT
- Audit events created for alert assignments

## Database Schema

All required tables from TASK-1 are used:
- `users`: User accounts with roles
- `session_records`: JWT session tracking with revocation support
- `customers`: Customer profiles
- `accounts`: Customer accounts
- `transactions`: Financial transactions
- `detection_rule_snapshots`: Historical rule versions
- `alerts`: Alert queue with status, priority, assignment, triage fields
- `audit_events`: Audit trail for assignments and actions

## Testing

Unit tests created:
- `backend/tests/test_auth_service.py` (to be implemented)
- `backend/tests/test_alert_service.py` (to be implemented)

Integration tests created:
- `backend/tests/test_auth_integration.py` (to be implemented)
- `backend/tests/test_alert_integration.py` (to be implemented)

## Next Steps

This task provides the foundation for:
- Alert triage disposition (FR-004)
- Alert-to-case escalation (FR-003)
- Case workspace features (FR-006, FR-007, FR-008, FR-010)
- Information requests (FR-016, FR-017, FR-018)
- Review handoff (FR-021)
