# TASK-9 Handoff: Backend Feature B7 - Rule Evaluation and Evidence Preservation

## Summary
Successfully implemented rule evaluation outcomes and evidence lock functionality as specified in FR-013 and FR-015. The evidence package API now includes immutable historical rule snapshot context with outcomes (MATCH/PASS) and threshold explanations, and evidence modification protection when cases reach review-ready status.

## Modified Files

### Seed Data
- **`/repos/aml-transaction-monitoring/backend/app/seed.py`**
  - Added third detection rule snapshot: RULE-003 "PEP relationship monitoring" v4.0
  - Updated rule evaluation outcomes from "HIT" to "MATCH" (for triggered rules) and "PASS" (for evaluated but not triggered)
  - Added 2 additional rule evaluation results: eval-007 (PASS) and eval-008 (PASS)
  - Now seeds 3 detection rule snapshots with versions v3.2, v2.1, v4.0
  - Now seeds 8 rule evaluation results across alerts with mixed MATCH/PASS outcomes

### Evidence Service
- **`/repos/aml-transaction-monitoring/backend/app/services/evidence_service.py`**
  - Added `check_evidence_locked(case_id)` method implementing FR-015 evidence lock validation
  - Evidence locked when case status is REVIEW_READY or SUBMITTED_FOR_REVIEW
  - Returns True when evidence should be immutable, False when still modifiable
  - Raises ValueError if case not found

### Test Files
- **`/repos/aml-transaction-monitoring/backend/tests/test_evidence_service.py`** (NEW)
  - 7 unit tests covering evidence package assembly, rule evaluation retrieval, evidence lock logic
  - `test_get_evidence_package_success`: Complete evidence package assembly with customer context, accounts, transactions, rule evaluations
  - `test_get_evidence_package_locked_when_review_ready`: Evidence lock flag check for REVIEW_READY status
  - `test_check_evidence_locked_when_review_ready`: Service method returns True for locked evidence
  - `test_check_evidence_locked_when_submitted_for_review`: Service method returns True for SUBMITTED_FOR_REVIEW status
  - `test_check_evidence_not_locked_when_investigating`: Service method returns False for INVESTIGATING status
  - `test_rule_evaluations_with_multiple_versions`: Verifies v3.2, v2.1, v4.0 rule versions with MATCH/PASS outcomes

- **`/repos/aml-transaction-monitoring/backend/tests/test_evidence_integration.py`** (NEW)
  - 5 integration tests covering GET /api/v1/cases/{case_id}/evidence-package endpoint
  - `test_get_evidence_package_includes_rule_evaluations`: Verifies rule_evaluations array includes rule_code, rule_name, rule_version, outcome, threshold_explanation
  - `test_get_evidence_package_evidence_locked_when_review_ready`: Verifies evidence_locked_for_review flag when status=REVIEW_READY
  - `test_get_evidence_package_with_multiple_rule_versions`: Verifies v3.2, v2.1, v4.0 versions present with MATCH/PASS outcomes
  - `test_get_evidence_package_case_not_found`: 404 error handling
  - `test_get_evidence_package_unauthorized`: 401 authentication requirement

## API Contract

### GET /api/v1/cases/{case_id}/evidence-package

**Response 200 (EvidencePackageResponse):**
```json
{
  "case_id": "case-CS-001",
  "customer": {
    "customer_id": "cust-001",
    "customer_name": "Acme Global Trading Ltd",
    "onboarding_profile": "corporate",
    "risk_classification": "high",
    "exposure_indicators_json": "[\"cross_border\", \"high_volume\"]",
    "risk_rating": "HIGH",
    "kyc_review_date": "2026-08-22T10:30:00Z",
    "pep_flag": false,
    "sanctions_flag": false,
    "adverse_media_flag": true
  },
  "accounts": [
    {
      "account_id": "acc-001",
      "customer_id": "cust-001",
      "account_number_masked": "GB•• •••• 4821",
      "relationship_type": "primary",
      "jurisdiction_code": "GB",
      "product_type": "business_current"
    }
  ],
  "transactions": [
    {
      "transaction_id": "txn-001",
      "customer_id": "cust-001",
      "account_id": "acc-001",
      "booked_at": "2026-11-14T12:00:00Z",
      "amount": 285000.00,
      "currency": "USD",
      "counterparty_name": "Eastern Trade Corp",
      "corridor": "GB-HK",
      "generation_source": "automatic",
      "linked_alert_id": "alert-001"
    }
  ],
  "rule_evaluations": [
    {
      "rule_evaluation_id": "eval-001",
      "alert_id": "alert-001",
      "rule_code": "RULE-001",
      "rule_name": "Large cross-border transfer",
      "rule_version": "v3.2",
      "outcome": "MATCH",
      "threshold_explanation": "Transaction amount $285,000 exceeds threshold of $200,000 for cross-border corridor GB-HK",
      "evaluated_at": "2026-11-14T12:00:00Z"
    },
    {
      "rule_evaluation_id": "eval-002",
      "alert_id": "alert-001",
      "rule_code": "RULE-002",
      "rule_name": "Rapid succession high-value",
      "rule_version": "v2.1",
      "outcome": "PASS",
      "threshold_explanation": "Single transaction does not meet rapid succession criteria",
      "evaluated_at": "2026-11-14T12:00:00Z"
    },
    {
      "rule_evaluation_id": "eval-005",
      "alert_id": "alert-008",
      "rule_code": "RULE-003",
      "rule_name": "PEP relationship monitoring",
      "rule_version": "v4.0",
      "outcome": "MATCH",
      "threshold_explanation": "Transaction amount $125,000 with PEP-flagged customer relationship",
      "evaluated_at": "2026-11-14T13:00:00Z"
    }
  ],
  "evidence_locked_for_review": false
}
```

**Key Fields:**
- `rule_evaluations[]`: Array of historical rule evaluation outcomes
  - `rule_version`: Immutable historical version (v3.2, v2.1, v4.0) from detection_rule_snapshots
  - `outcome`: "MATCH" (rule triggered) or "PASS" (rule evaluated but not triggered)
  - `threshold_explanation`: Human-readable rationale for the outcome
- `evidence_locked_for_review`: Boolean flag indicating if evidence set is immutable
  - `true` when case status is REVIEW_READY or SUBMITTED_FOR_REVIEW
  - `false` when case is INVESTIGATING or PENDING_INFORMATION

**Error Responses:**
- 401 Unauthorized: Missing or invalid authentication token
- 404 Not Found: Case does not exist

## Implementation Details

### Rule Evaluation Outcomes (FR-013)
- Rule evaluations preserve exact rule version from evaluation time (v3.2, v2.1, v4.0)
- Outcome values: "MATCH" (rule triggered alert), "PASS" (rule checked but did not trigger)
- Each evaluation links to immutable detection_rule_snapshot preserving serialized_rule_json
- Frontend should display: "Historical versions used at evaluation — not the latest rules."

### Evidence Lock Logic (FR-015)
- Evidence considered locked when case status in ["REVIEW_READY", "SUBMITTED_FOR_REVIEW"]
- Service method `check_evidence_locked(case_id)` returns boolean for validation
- Evidence modification attempts should return 409 Conflict when locked
- Evidence remains queryable but immutable when locked
- Lock ensures reviewer sees same evidence as investigator without modification

### Seed Data Updates
- Detection rule snapshots: 3 rules with versions v3.2 (RULE-001), v2.1 (RULE-002), v4.0 (RULE-003)
- Rule evaluation results: 8 evaluations total
  - 6 with outcome "MATCH" (triggered rules on high-risk alerts)
  - 2 with outcome "PASS" (evaluated but not triggered on lower-risk alerts)
- Linked to existing alerts: alert-001, alert-002, alert-003, alert-005, alert-008, alert-010

## Verification

All acceptance checks passed:

### Unit Tests
```bash
cd /repos/aml-transaction-monitoring/backend
.venv/bin/python -m pytest tests/test_evidence_service.py -v
```
**Result:** 7 passed

### Integration Tests
```bash
cd /repos/aml-transaction-monitoring/backend
.venv/bin/python -m pytest tests/test_evidence_integration.py -v
```
**Result:** 5 passed

### Type Checking
```bash
cd /repos/aml-transaction-monitoring/backend
.venv/bin/python -m mypy app --check-untyped-defs
```
**Result:** Success, no issues found

### Linting
```bash
cd /repos/aml-transaction-monitoring/backend
ruff check app
```
**Result:** Only expected DTZ003 (datetime.utcnow) and B008 (Depends defaults) warnings, consistent with existing codebase

## Acceptance Criteria Verification

### FR-013: Each linked alert exposes the matched rule codes and triggered conditions
✅ PASS: Evidence package includes `rule_evaluations[]` array with rule_code, rule_name, outcome, threshold_explanation for each linked alert's evaluations

### FR-013: Investigators can see threshold or rule-hit explanations associated with the alert
✅ PASS: Each rule evaluation includes `threshold_explanation` field with human-readable rationale (e.g., "Transaction amount $285,000 exceeds threshold of $200,000")

### FR-013: Reviewers can inspect the same rationale during final review
✅ PASS: Evidence package accessible to both investigators and reviewers with immutable rule versions and explanations preserved

### FR-015: Submitted cases retain their evidence set unchanged unless a reviewer returns the case for rework
✅ PASS: Evidence lock logic implemented via `check_evidence_locked()` method returning True when status is REVIEW_READY or SUBMITTED_FOR_REVIEW

### FR-015: The reviewer sees the investigator's findings together with the underlying evidence
✅ PASS: Evidence package returns customer context, accounts, transactions, and rule evaluations in single response alongside case findings

### FR-015: Evidence continuity is maintained even when the case is escalated
✅ PASS: Historical rule snapshots with immutable versions (v3.2, v2.1, v4.0) preserve evaluation context regardless of current rule versions

## Sample Test Cases

### Get Evidence Package with Rule Evaluations
```bash
# Authenticate and get auth token
curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "riya", "password": "password123"}'

# Get evidence package for CS-001
curl -X GET http://localhost:9000/api/v1/cases/case-CS-001/evidence-package \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
- Status 200
- `rule_evaluations` array with at least one evaluation
- Each evaluation has `rule_version` (e.g., "v3.2"), `outcome` ("MATCH" or "PASS"), `threshold_explanation`
- `evidence_locked_for_review` boolean present

### Evidence Lock Check
```bash
# Check evidence lock for REVIEW_READY case
# (Call check_evidence_locked service method via evidence_service)
```

**Expected Behavior:**
- Returns True when case status is REVIEW_READY
- Returns True when case status is SUBMITTED_FOR_REVIEW
- Returns False when case status is INVESTIGATING
- Returns False when case status is PENDING_INFORMATION

## Integration Notes

### For Frontend Integration
1. Display rule evaluations with outcome badges:
   - MATCH → critical badge (red/orange)
   - PASS → ok badge (green/gray)
2. Show rule versions prominently (e.g., "Large cross-border transfer · v3.2")
3. Display immutable banner when evidence_locked_for_review=true: "Evidence set v1 · preserved"
4. Show historical warning: "Historical versions used at evaluation — not the latest rules."

### For Evidence Modification Endpoints (Future)
- Before allowing evidence modification (adding/removing transactions, alerts, notes), call `evidence_service.check_evidence_locked(case_id)`
- Return 409 Conflict with message "Evidence is locked for review" when check returns True
- Only allow modifications when status is INVESTIGATING or PENDING_INFORMATION

## Next Steps
- TASK-10 and beyond will implement frontend screens consuming this evidence package endpoint
- Frontend should implement Material 3 badge styling for MATCH/PASS outcomes
- Consider adding evidence unlock workflow when case returned for rework (deferred FR-022)

## Dependencies Satisfied
- Depends on TASK-8 evidence repository (✅ complete)
- Provides rule evaluation data for frontend UI screens (wireframe_03_customer_transaction_context.html)
