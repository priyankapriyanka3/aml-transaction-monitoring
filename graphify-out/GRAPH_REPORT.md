# Graph Report - aml-transaction-monitoring  (2026-11-21)

## Corpus Check
- 164 files · ~107,593 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 34 file(s) not represented in the graph (top: .db 17, (none) 5, .ini 2)

## Summary
- 1521 nodes · 3385 edges · 114 communities (61 shown, 53 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 257 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a2da3f9b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- AML Transaction Monitoring & Compliance Workbench
- test_pipeline_migration_parity.py
- utils.ts
- TASK-9 Handoff: Backend Feature B7 - Rule Evaluation and Evidence Preservation
- alert_schemas.py
- main.py
- aml-backend
- devDependencies
- utils.ts
- .get_overview
- compilerOptions
- compilerOptions
- TASK-4 Handoff: Backend Feature B2 - Case Creation and Overview
- AuthService
- Implementation Details
- pytest
- test_auth_integration.py
- handoff_service.py
- information_requests.py
- TASK-3 Handoff: Backend Feature B1 - Alert Queue and Assignment
- User
- CaseRepository
- SessionRecord
- TASK-8 Handoff: Backend Feature B6 - Customer and Transaction Evidence
- scripts
- .login
- test_get_alerts_endpoint
- fixture
- Task 14: Integration and End-to-End Testing - Handoff Report
- test_check_evidence_locked_when_review_ready
- TASK-6 Handoff: Backend Feature B4 - Case Status Transitions and Information Request Issuance
- CaseWorkspacePage.tsx
- AuditEvent
- steps
- TASK-10 Handoff: Information Request Response and SLA Tracking
- claim_alert
- InformationRequestsPage.tsx
- EvidenceRepository
- UserRepository
- ApiClient
- test_get_alerts_filter_by_status
- TASK-7 Handoff: Backend Feature B5 - Recommendation Submission and Review Handoff
- AlertService
- environment
- AlertRepository
- package.json
- datetime
- AlertQueuePage.tsx
- run_task6_tests.sh
- App.tsx
- auth.py
- test_get_alerts_filter_by_priority
- ReviewHandoffPage.tsx
- test_evidence_service.py
- test_get_alerts_filter_by_assignee
- test_get_alerts_filter_by_risk_score
- test_get_alerts_pagination
- AMLCase
- .list_notes
- journey_alert_to_recommend-56c21-rom-alert-to-recommendation/error-context.md
- test_health_integration.py
- cases.py
- journey_information_reques-92e1e-d-unblocking-recommendation/error-context.md
- CaseService
- wireframe_01_alert_queue-W-5b9a1-with-filters-and-pagination/error-context.md
- auth_middleware.py
- playwright.config.ts
- test_get_alerts_sorting
- vite
- test_get_alerts_enrichment
- start.sh
- API Endpoints
- @playwright/test
- Database Migrations
- Troubleshooting
- Quick Start
- Manual Development Setup
- Running Tests
- Docker Deployment
- 70e3a29542df_initial_schema_with_all_15_tables.py
- PaginatedResponse
- test_claim_alert_endpoint
- vitest
- Environment Variables
- CI/CD Pipeline
- test_claim_alert_nonexistent
- docker-entrypoint.sh script
- test_post_case_note_case_not_found
- test_claim_alert_invalid_assignee
- test_claim_alert_without_auth
- stop.sh
- test_alert_workflow_integration

## God Nodes (most connected - your core abstractions)
1. `User` - 115 edges
2. `AMLCase` - 96 edges
3. `Alert` - 76 edges
4. `Customer` - 68 edges
5. `Transaction` - 67 edges
6. `CaseAlertLink` - 49 edges
7. `Account` - 47 edges
8. `CaseService` - 44 edges
9. `InformationRequest` - 36 edges
10. `Base` - 35 edges

## Surprising Connections (you probably didn't know these)
- `Security Notes` --references--> `get_current_user()`  [INFERRED]
  .handoff/TASK-8.md → backend/app/middleware/auth_middleware.py
- `Design System` --references--> `RequireAuth()`  [INFERRED]
  README.md → frontend/src/components/auth/RequireAuth.tsx
- `Test Files` --references--> `test_get_evidence_package_evidence_locked_when_review_ready()`  [INFERRED]
  .handoff/TASK-9.md → backend/tests/test_evidence_integration.py
- `Test Files` --references--> `test_get_evidence_package_unauthorized()`  [INFERRED]
  .handoff/TASK-9.md → backend/tests/test_evidence_integration.py
- `Test Files` --references--> `test_check_evidence_locked_when_review_ready()`  [INFERRED]
  .handoff/TASK-9.md → backend/tests/test_evidence_service.py

## Import Cycles
- None detected.

## Communities (114 total, 53 thin omitted)

### Community 0 - "AML Transaction Monitoring & Compliance Workbench"
Cohesion: 0.20
Nodes (9): AML Transaction Monitoring & Compliance Workbench, Architecture, Contributing, Database Schema, Development Workflow, License, Project Structure, Security Features (+1 more)

### Community 1 - "test_pipeline_migration_parity.py"
Cohesion: 0.08
Nodes (20): run_migrations_offline(), run_migrations_online(), _alembic(), _annotation_kind(), _column_kind(), _env_py_text(), _foreign_key(), _has_alembic_version() (+12 more)

### Community 2 - "utils.ts"
Cohesion: 0.15
Nodes (17): AccountRelationshipList(), AccountRelationshipListProps, CustomerRiskPanel(), CustomerRiskPanelProps, RuleEvaluationOutcomeRow(), RuleEvaluationOutcomeRowProps, SortBy, SortDirection (+9 more)

### Community 3 - "TASK-9 Handoff: Backend Feature B7 - Rule Evaluation and Evidence Preservation"
Cohesion: 0.06
Nodes (31): Acceptance Criteria Verification, API Contract, Dependencies Satisfied, Evidence Lock Check, Evidence Lock Logic (FR-015), Evidence Service, For Evidence Modification Endpoints (Future), For Frontend Integration (+23 more)

### Community 4 - "alert_schemas.py"
Cohesion: 0.18
Nodes (7): AlertQueueFilters, AlertQueueResponse, AlertResponse, ClaimRequest, ClaimResponse, TriageDispositionRequest, TriageDispositionResponse

### Community 5 - "main.py"
Cohesion: 0.08
Nodes (7): Settings, health_check(), lifespan(), general_exception_handler(), http_exception_handler(), validation_exception_handler(), get_readiness()

### Community 9 - "devDependencies"
Cohesion: 0.12
Nodes (16): devDependencies, @playwright/test@^1.49.0, tailwindcss@^3.4.15, @testing-library/jest-dom@^6.1.5, @testing-library/react@^14.1.2, @types/node@^26.6.6, @types/react@^18.3.12, @types/react-dom@^18.3.1 (+8 more)

### Community 10 - "utils.ts"
Cohesion: 0.22
Nodes (9): dependencies, clsx@^2.1.1, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, tailwind-merge@^2.5.2, clsx, react-dom (+1 more)

### Community 11 - ".get_overview"
Cohesion: 0.09
Nodes (9): create_case_note(), get_case_notes(), get_case_overview(), get_handoff_package(), RecommendationSubmitRequest, StatusTransitionRequest, submit_handoff(), submit_recommendation() (+1 more)

### Community 12 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 13 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, allowSyntheticDefaultImports, composite, lib, module, moduleResolution, noUnusedLocals, noUnusedParameters (+5 more)

### Community 14 - "TASK-4 Handoff: Backend Feature B2 - Case Creation and Overview"
Cohesion: 0.09
Nodes (21): Acceptance Criteria Coverage, Case Creation Flow, Case CS-001, Case CS-002, Case Overview Assembly, Created, Database Tables Used, Files Modified/Created (+13 more)

### Community 15 - "AuthService"
Cohesion: 0.13
Nodes (10): AuthService, seeded_user(), test_login_inactive_user(), test_login_success(), test_logout_invalid_session(), test_logout_success(), test_password_hashing(), test_validate_token_invalid() (+2 more)

### Community 16 - "Implementation Details"
Cohesion: 0.12
Nodes (16): API Contract Summary, GET /api/v1/cases/{case_id}/notes, Implementation Details, Implemented Endpoints, Integration Tests (test_triage_integration.py), New Repository: CaseNoteRepository, POST /api/v1/alerts/{alert_id}/triage-disposition, POST /api/v1/cases/{case_id}/notes (+8 more)

### Community 22 - "pytest"
Cohesion: 0.10
Nodes (13): AlertService, test_claim_alert_invalid_assignee(), test_claim_alert_nonexistent(), test_claim_alert_reassignment(), test_claim_alert_success(), test_save_triage_disposition_alert_not_found(), test_save_triage_disposition_close_non_actionable(), test_save_triage_disposition_creates_audit_event() (+5 more)

### Community 23 - "test_auth_integration.py"
Cohesion: 0.10
Nodes (10): test_auth_flow_end_to_end(), test_login_endpoint_invalid_credentials(), test_login_endpoint_nonexistent_user(), test_login_endpoint_success(), test_login_endpoint_validation_error(), test_logout_endpoint_invalid_session(), test_logout_endpoint_success(), test_protected_endpoint_with_invalid_token() (+2 more)

### Community 24 - "handoff_service.py"
Cohesion: 0.13
Nodes (9): HandoffPackageResponse, HandoffSubmitRequest, HandoffSubmitResponse, InformationRequestSummary, LinkedAlertSummary, ReadinessChecklistItem, ReadinessResponse, HandoffService (+1 more)

### Community 25 - "information_requests.py"
Cohesion: 0.14
Nodes (5): create_information_request(), list_information_requests(), record_information_request_response(), InformationRequestCreateRequest, RecordResponseRequest

### Community 26 - "TASK-3 Handoff: Backend Feature B1 - Alert Queue and Assignment"
Cohesion: 0.11
Nodes (17): Alert Endpoints, Authentication Endpoints, Authentication Flow, Database Schema, GET /api/v1/alerts, Implemented Endpoints, Next Steps, POST /api/v1/alerts/{alert_id}/claim (+9 more)

### Community 27 - "User"
Cohesion: 0.06
Nodes (27): InformationRequest, User, InformationRequestService, test_complete_workflow_request_to_response(), test_create_information_request_success(), test_create_information_request_validates_due_at_future(), test_create_information_request_validates_requested_summary(), test_list_information_requests_by_case() (+19 more)

### Community 30 - "TASK-8 Handoff: Backend Feature B6 - Customer and Transaction Evidence"
Cohesion: 0.08
Nodes (24): Acceptance Criteria Verification, API Endpoints, Configuration, Data Model Changes, Dependencies Met, FR-011: Account Relationships, FR-011: Customer Context, FR-012: Transaction Evidence Timeline (+16 more)

### Community 31 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test, type-check

### Community 41 - "fixture"
Cohesion: 0.22
Nodes (5): auth_client(), client(), db_session(), _fresh_schema(), auth_headers()

### Community 42 - "Task 14: Integration and End-to-End Testing - Handoff Report"
Cohesion: 0.10
Nodes (19): Acceptance Checks Status, ✅ Backend Tests (158/158 passing), Blocker Analysis, Conclusion, Files Modified/Created in This Task, Frontend Test Infrastructure, ✅ Frontend Unit Tests (1/1 passing), ❌ Journey E2E Tests (0/2 passing) (+11 more)

### Community 43 - "test_check_evidence_locked_when_review_ready"
Cohesion: 0.25
Nodes (3): test_check_evidence_locked_when_review_ready(), test_check_evidence_locked_when_submitted_for_review(), test_check_evidence_not_locked_when_investigating()

### Community 44 - "TASK-6 Handoff: Backend Feature B4 - Case Status Transitions and Information Request Issuance"
Cohesion: 0.09
Nodes (21): API Endpoints Implemented, Audit Trail, Dependencies, Files Created/Modified, GET /api/v1/information-requests?case_id={case_id}, Implementation Summary, Integration Tests (test_information_request_integration.py), IR-001 (Open, Not Overdue) (+13 more)

### Community 45 - "CaseWorkspacePage.tsx"
Cohesion: 0.22
Nodes (15): CaseHeader(), CaseHeaderProps, InvestigationNotesPanel(), InvestigationNotesPanelProps, RecommendationPanel(), RecommendationPanelProps, formatDateTime(), CaseWorkspacePage() (+7 more)

### Community 47 - "AuditEvent"
Cohesion: 0.08
Nodes (11): AuditEvent, AuditEventRepository, get_audit_events(), AuditService, test_get_audit_events_combined_filters(), test_get_audit_events_filter_by_action_type(), test_get_audit_events_filter_by_entity_id(), test_get_audit_events_filter_by_entity_type() (+3 more)

### Community 48 - "steps"
Cohesion: 0.07
Nodes (33): runs-on, services, steps, DATABASE_URL, POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, runs-on (+25 more)

### Community 49 - "TASK-10 Handoff: Information Request Response and SLA Tracking"
Cohesion: 0.06
Nodes (30): 1. Information Request Response Recording, 2. Information Request List with SLA Tracking, 3. Audit Events Retrieval, 4. Health/Readiness Endpoint, Acceptance Criteria Met, API Contract Summary, Audit Trail, Case Status Transitions (+22 more)

### Community 50 - "claim_alert"
Cohesion: 0.20
Nodes (4): claim_alert(), create_case_from_alert(), get_alert_queue(), save_triage_disposition()

### Community 51 - "InformationRequestsPage.tsx"
Cohesion: 0.13
Nodes (16): DecisionBlockerBanner(), DecisionBlockerBannerProps, InformationRequestForm(), InformationRequestFormProps, InformationRequestHistoryList(), InformationRequestHistoryListProps, apiClient, ApiError (+8 more)

### Community 57 - "TASK-7 Handoff: Backend Feature B5 - Recommendation Submission and Review Handoff"
Cohesion: 0.08
Nodes (24): API Endpoints, Audit Events, CASE_HANDOFF_SUBMITTED, CaseRepository, Dependencies, GET /api/v1/cases/{case_id}/handoff, Handoff Submission, HandoffService (`backend/app/services/handoff_service.py`) (+16 more)

### Community 58 - "AlertService"
Cohesion: 0.13
Nodes (7): test_get_queue_all_alerts(), test_get_queue_filter_by_assignee(), test_get_queue_filter_by_priority(), test_get_queue_filter_by_risk_score(), test_get_queue_filter_by_status(), test_get_queue_pagination(), test_get_queue_sorting()

### Community 59 - "environment"
Cohesion: 0.08
Nodes (26): BACKEND_HOST, build, environment, ports, volumes, x-preview-port, args, context (+18 more)

### Community 61 - "package.json"
Cohesion: 0.14
Nodes (13): autoprefixer@^10.4.20, jsdom@^23.0.1, postcss@^8.4.49, engines, node, npm, name, private (+5 more)

### Community 62 - "datetime"
Cohesion: 0.12
Nodes (7): downgrade(), upgrade(), Base, get_db(), CaseDecision, CaseNote, InformationRequestResponse

### Community 63 - "AlertQueuePage.tsx"
Cohesion: 0.19
Nodes (17): AlertFilterBar(), AlertFilterBarProps, FilterChip(), FilterChipProps, HeroAlertCard(), HeroAlertCardProps, TriageDispositionModal(), TriageDispositionModalProps (+9 more)

### Community 66 - "App.tsx"
Cohesion: 0.17
Nodes (16): App(), RequireAuth(), RequireAuthProps, AuthContext, AuthContextType, AuthProvider(), AuthProviderProps, useAuth() (+8 more)

### Community 67 - "auth.py"
Cohesion: 0.19
Nodes (6): login(), logout(), LoginRequest, LoginResponse, LogoutRequest, UserResponse

### Community 69 - "ReviewHandoffPage.tsx"
Cohesion: 0.10
Nodes (20): FourEyesSegregationCard(), FourEyesSegregationCardProps, Officer, ReadinessChecklistCard(), ReadinessChecklistCardProps, AmlTopBar(), AmlTopBarProps, ActionButtonProps (+12 more)

### Community 70 - "test_evidence_service.py"
Cohesion: 0.12
Nodes (13): DetectionRuleSnapshot, RiskProfile, RuleEvaluationResult, seed_database(), test_get_evidence_package_case_not_found(), test_get_evidence_package_includes_rule_evaluations(), test_get_evidence_package_with_multiple_rule_versions(), test_get_evidence_package_success() (+5 more)

### Community 75 - "AMLCase"
Cohesion: 0.06
Nodes (50): Account, Alert, AMLCase, CaseAlertLink, Customer, Transaction, test_fr003_case_creation_preserves_alert_identifier(), test_fr003_case_shows_linked_alert() (+42 more)

### Community 77 - "journey_alert_to_recommend-56c21-rom-alert-to-recommendation/error-context.md"
Cohesion: 0.33
Nodes (5): Error details, Instructions, Page snapshot, Test info, Test source

### Community 78 - "test_health_integration.py"
Cohesion: 0.20
Nodes (4): test_health_ready_database_connection_check(), test_health_ready_endpoint_accessible(), test_health_ready_returns_expected_fields(), test_health_ready_timestamp_format()

### Community 79 - "cases.py"
Cohesion: 0.11
Nodes (12): get_evidence_package(), CaseNoteRequest, CaseNoteResponse, CaseOverviewResponse, CreateCaseFromAlertRequest, AccountResponse, CustomerContextResponse, EvidencePackageResponse (+4 more)

### Community 80 - "journey_information_reques-92e1e-d-unblocking-recommendation/error-context.md"
Cohesion: 0.40
Nodes (4): Error details, Instructions, Test info, Test source

### Community 81 - "CaseService"
Cohesion: 0.13
Nodes (11): CaseService, test_create_case_from_alert_alert_not_found(), test_get_case_overview_case_not_found(), test_submit_recommendation_requires_linked_alert(), test_transition_case_not_found(), test_transition_invalid_from_investigating_to_submitted(), test_transition_invalid_from_pending_information_to_review_ready(), test_transition_investigating_to_pending_information() (+3 more)

### Community 82 - "wireframe_01_alert_queue-W-5b9a1-with-filters-and-pagination/error-context.md"
Cohesion: 0.40
Nodes (4): Error details, Instructions, Test info, Test source

### Community 84 - "playwright.config.ts"
Cohesion: 0.20
Nodes (7): backendDir, __dirname, E2E_ACTION_TIMEOUT, E2E_NAVIGATION_TIMEOUT, E2E_TEST_TIMEOUT, __filename, venvPython

### Community 87 - "vite"
Cohesion: 0.40
Nodes (4): vite@^6.0.1, @vitejs/plugin-react@^4.3.4, vite, @vitejs/plugin-react

### Community 89 - "start.sh"
Cohesion: 0.43
Nodes (7): check_prerequisites(), DATABASE_URL, find_available_port(), native_path(), port_in_use(), portable_sed(), start.sh script

### Community 90 - "API Endpoints"
Cohesion: 0.29
Nodes (7): Alerts, API Endpoints, Audit, Authentication, Cases, Health, Information Requests

### Community 92 - "Database Migrations"
Cohesion: 0.40
Nodes (5): Apply migrations, Check migration status, Create a new migration, Database Migrations, Rollback one migration

### Community 93 - "Troubleshooting"
Cohesion: 0.40
Nodes (5): Database migration errors, Frontend build errors, Port already in use, Troubleshooting, Windows-specific issues

### Community 94 - "Quick Start"
Cohesion: 0.40
Nodes (5): Default Credentials, One-Command Startup, Prerequisites, Quick Start, Stopping Services

### Community 95 - "Manual Development Setup"
Cohesion: 0.50
Nodes (4): 1. Backend Setup, 2. Frontend Setup, 3. Running the Application Manually, Manual Development Setup

### Community 96 - "Running Tests"
Cohesion: 0.50
Nodes (4): Backend Tests, End-to-End Tests, Frontend Tests, Running Tests

### Community 97 - "Docker Deployment"
Cohesion: 0.50
Nodes (4): Building Images, Docker Deployment, PostgreSQL Deployment, Running with Docker Compose

### Community 102 - "Environment Variables"
Cohesion: 0.67
Nodes (3): Backend, Environment Variables, Frontend

### Community 103 - "CI/CD Pipeline"
Cohesion: 0.67
Nodes (3): Backend Job, CI/CD Pipeline, Frontend Job

## Knowledge Gaps
- **2 isolated node(s):** `aml-backend`, `DATABASE_URL`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 761 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **53 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `.login`, `alert_schemas.py`, `test_evidence_service.py`, `fixture`, `.get_overview`, `AMLCase`, `cases.py`, `AuthService`, `AuditEvent`, `CaseService`, `auth_middleware.py`, `UserRepository`, `test_auth_integration.py`, `pytest`, `datetime`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `User` (e.g. with `get_current_user()` and `UserRepository`) actually correct?**
  _`User` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `aml-backend`, `DATABASE_URL` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_pipeline_migration_parity.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08292682926829269 - nodes in this community are weakly interconnected._
- **Why does `AMLCase` connect `AMLCase` to `test_evidence_service.py`, `.get_overview`, `test_check_evidence_locked_when_review_ready`, `.create_case_from_alert`, `CaseService`, `User`, `CaseRepository`, `datetime`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `AMLCase` (e.g. with `CaseService` and `test_create_case_from_alert_success()`) actually correct?**
  _`AMLCase` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `TASK-9 Handoff: Backend Feature B7 - Rule Evaluation and Evidence Preservation` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._