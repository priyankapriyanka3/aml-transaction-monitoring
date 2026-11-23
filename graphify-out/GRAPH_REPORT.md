# Graph Report - aml-transaction-monitoring  (2026-11-22)

## Corpus Check
- 168 files · ~74,977 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 29 file(s) not represented in the graph (top: .pro 8, (none) 5, .xml 4)

## Summary
- 1823 nodes · 3735 edges · 124 communities (72 shown, 52 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 234 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a2da3f9b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- AML Transaction Monitoring & Compliance Workbench
- AmlCase
- TASK-8 Backend Handoff: Decision Blocker Enforcement and Officer Review
- Session
- test_pipeline_seed_runs.py
- AmlHeroAlertCard.kt
- BaseModel
- Stack Deviation Notice
- TASK-6 Handoff: Investigation Notes and Case Workspace
- AML Workbench Backend
- frontend/package.json
- start.sh
- stop.sh
- aml-workbench-backend
- Android Design System Implementation Verification
- test_alert_service.py
- AML Workbench Android Application
- EvidenceScreen.kt
- seed.py
- TASK-3 Backend Alert API Handoff
- Alert
- UUID
- InformationRequest
- EvidenceViewModelTest.kt
- Theme.kt
- security.py
- TASK-10: Backend Feature B8 - Independent Officer Assignment and Final Decision Recording
- TASK-9 Handoff: Information Request Response Recording and Readiness Verification
- Frontend Implementation Summary
- AlertQueueViewModelTest
- conftest.py
- requests.py
- Settings
- TASK-4 Handoff: Transaction Evidence and Case Creation
- AML Transaction Monitoring Workbench - Frontend
- User
- TASK-5: Backend Feature B3 - Historical Rule Snapshots and Linked Alerts
- EvidenceGap
- cases.py
- 20261122_1400_005_create_case_notes_table.py
- with
- decision_service.py
- Frontend Navigation Structure
- Development Workflow
- AmlReadinessChecklist.kt
- TASK-7 Backend Handoff: Evidence Gap Tracking and Information Request Creation
- AmlDecisionBlockerBanner.kt
- 20261122_1400_001_create_users_and_sessions.py
- Key Navigation Elements
- AmlDecisionSelector.kt
- AlertRepository
- AmlRuleOutcomeRow.kt
- AlertQueueViewModel.kt
- test_audit_trail_integration.py
- AmlDimens
- compilerOptions
- api.ts
- test_case_service.py
- OfficerReviewPage.tsx
- routers/auth.py
- Alerts Feature Module
- AlertEvidence
- App.tsx
- AlertDto.kt
- EvidenceViewModel
- ApiClient
- package.json
- AlertQueueEvent
- compilerOptions
- EvidenceEvent
- alerts.py
- dependencies
- ReadinessRepository
- API Routes
- CaseInvestigationPage.tsx
- Database Migrations
- 20261122_1400_002_create_alert_tables.py
- main.py
- test_four_eyes_integration.py
- Security
- test_full_flow_integration.py
- test_pipeline_migration_parity.py
- _mapped_columns
- env.py
- middleware/auth.py
- information_request_service.py
- Testing
- 20261122_1400_004_create_rule_snapshots_table.py
- 20261122_1400_006_create_evidence_gap_tables.py
- Troubleshooting
- Database Schema
- Dependencies
- Installation
- 20261122_1400_003_create_case_tables.py
- 20261122_1400_007_create_assignment_decision_tables.py
- Code Quality

## God Nodes (most connected - your core abstractions)
1. `User` - 92 edges
2. `Session` - 69 edges
3. `hash_password()` - 59 edges
4. `Alert` - 57 edges
5. `Customer` - 53 edges
6. `Transaction` - 53 edges
7. `Account` - 51 edges
8. `AmlCase` - 50 edges
9. `Base` - 38 edges
10. `CaseAlertLink` - 33 edges

## Surprising Connections (you probably didn't know these)
- `5. Seed Data` --references--> `seed_rule_snapshots()`  [INFERRED]
  .handoff/TASK-5.md → backend/app/seed.py
- `Models` --references--> `RequestAttachment`  [INFERRED]
  .handoff/TASK-7.md → backend/app/models/request_attachment.py
- `Models` --references--> `InformationRequest`  [INFERRED]
  .handoff/TASK-7.md → backend/app/models/information_request.py
- `Test Files` --references--> `test_add_alert_link()`  [EXTRACTED]
  .handoff/TASK-5.md → backend/tests/test_case_service.py
- `Models` --references--> `EvidenceGap`  [INFERRED]
  .handoff/TASK-7.md → backend/app/models/evidence_gap.py

## Import Cycles
- None detected.

## Communities (124 total, 52 thin omitted)

### Community 0 - "AML Transaction Monitoring & Compliance Workbench"
Cohesion: 0.04
Nodes (45): 1. Clone the repository, 2. Start all services, 3. Login with seed credentials, 4. Stop all services, Additional Documentation, AML Transaction Monitoring & Compliance Workbench, API Documentation, Architecture (+37 more)

### Community 1 - "AmlCase"
Cohesion: 0.11
Nodes (10): CaseAlertLink, AmlCase, CaseNote, test_get_case_workspace(), test_get_case_workspace_not_found(), test_share_for_review_blocks_without_officer(), test_share_for_review_success(), test_get_officer_review_package_success() (+2 more)

### Community 2 - "TASK-8 Backend Handoff: Decision Blocker Enforcement and Officer Review"
Cohesion: 0.06
Nodes (30): 403 Forbidden - Four-Eyes Violation, 409 Conflict - Open Requests Blocker, 422 Unprocessable Entity - Invalid Outcome, 422 Unprocessable Entity - Missing Rationale, API Endpoints, Blocker Enforcement Flow, Blocker Enforcement Rules, Blocker State Values (+22 more)

### Community 3 - "Session"
Cohesion: 0.09
Nodes (12): Session, logout(), AuthService, test_authenticate_user_inactive(), test_authenticate_user_not_found(), test_authenticate_user_success(), test_authenticate_user_wrong_password(), test_create_session() (+4 more)

### Community 4 - "test_pipeline_seed_runs.py"
Cohesion: 0.29
Nodes (6): _env(), _is_async(), _run(), _seed_module(), seeded(), test_the_seed_runs_a_second_time()

### Community 6 - "BaseModel"
Cohesion: 0.14
Nodes (8): AlertQueueItem, AlertSummaryItem, DecisionRecordedResponse, NoteSummaryItem, OfficerReviewPackageResponse, RecordDecisionRequest, RequestSummaryItem, RuleSnapshotSummaryItem

### Community 7 - "Stack Deviation Notice"
Cohesion: 0.12
Nodes (15): Authentication, Backend (Python FastAPI), Database Schema, From Architecture (HLD/LLD), From Design System (design.md), From Requirements, Frontend (React + TypeScript), Infrastructure (+7 more)

### Community 8 - "TASK-6 Handoff: Investigation Notes and Case Workspace"
Cohesion: 0.12
Nodes (15): Acceptance Criteria Coverage, Adding Investigation Note, Audit Trail, case_notes Table, Database Schema, Example Flows, GET /api/v1/cases/{caseId}/workspace, Implemented Endpoints (+7 more)

### Community 9 - "AML Workbench Backend"
Cohesion: 0.14
Nodes (13): AML Workbench Backend, API Documentation, Database Seeding, Database URLs, Environment Configuration, Idempotent Seeding, License, Project Structure (+5 more)

### Community 10 - "frontend/package.json"
Cohesion: 0.07
Nodes (35): devDependencies, eslint@^8.55.0, eslint-plugin-react-hooks@^4.6.0, eslint-plugin-react-refresh@^0.4.5, @playwright/test@^1.40.1, @types/react@^18.2.43, @types/react-dom@^18.2.17, typescript@^5.2.2 (+27 more)

### Community 11 - "start.sh"
Cohesion: 0.39
Nodes (6): check_prerequisites(), DATABASE_URL, find_available_port(), native_path(), port_in_use(), start.sh script

### Community 20 - "Android Design System Implementation Verification"
Cohesion: 0.05
Nodes (41): 1. `./gradlew :core:designsystem:assembleDebug`, 2. `./gradlew :core:designsystem:lintDebug`, 3. Design tokens match design.md specification, 4.1: Hero Alert Card ✅, 4.2: Rule Evaluation Outcome Row ✅, 4.3: Decision Blocker Banner ✅, 4.4: Readiness Checklist ✅, 4.5: Four-Eyes Card ✅ (+33 more)

### Community 21 - "test_alert_service.py"
Cohesion: 0.10
Nodes (8): AlertRepository, AlertService, test_assign_alert_already_assigned_to_different_user(), test_assign_alert_idempotent(), test_assign_alert_success(), test_get_alert_queue_filters_by_ownership(), test_get_alert_queue_filters_by_priority(), test_get_alert_queue_returns_prioritized_list()

### Community 22 - "AML Workbench Android Application"
Cohesion: 0.07
Nodes (28): Adaptive Layouts, AML Workbench Android Application, Architecture, Build Commands, Building the Design System Module, Color Palette, Compliance Features, Compliance Status Colors (+20 more)

### Community 23 - "EvidenceScreen.kt"
Cohesion: 0.09
Nodes (5): EvidenceContent(), EvidenceScreen(), FactRow(), AlertQueueCard(), AlertQueueScreen()

### Community 26 - "seed.py"
Cohesion: 0.09
Nodes (3): Base, RequestAttachment, RuleEvaluationSnapshot

### Community 27 - "TASK-3 Backend Alert API Handoff"
Cohesion: 0.12
Nodes (16): Alert Assignment, API Base URL, Database Schema Changes, Default User Credentials, Foreign Key Relationships, GET /api/v1/alerts, Implemented Endpoints, Indexes Created (+8 more)

### Community 28 - "Alert"
Cohesion: 0.08
Nodes (25): Account, Alert, Customer, Transaction, test_assign_alert_already_assigned_conflict(), test_assign_alert_success(), test_get_alert_queue_pagination(), test_get_alert_queue_requires_auth() (+17 more)

### Community 29 - "UUID"
Cohesion: 0.09
Nodes (16): CaseDecision, CaseReviewAssignment, seed_accounts(), seed_alerts(), seed_all(), seed_case_notes(), seed_cases(), seed_customers() (+8 more)

### Community 36 - "security.py"
Cohesion: 0.09
Nodes (11): create_access_token(), decode_access_token(), hash_token(), verify_password(), test_create_and_decode_token(), test_get_me_endpoint(), test_get_me_endpoint_unauthorized(), test_hash_password() (+3 more)

### Community 37 - "TASK-10: Backend Feature B8 - Independent Officer Assignment and Final Decision Recording"
Cohesion: 0.06
Nodes (35): Audit Events, Blocker Enforcement, Blocker Resolution, Blocker State Management, Blocker States, case_decisions, case_review_assignments, Completed Decision (+27 more)

### Community 38 - "TASK-9 Handoff: Information Request Response Recording and Readiness Verification"
Cohesion: 0.07
Nodes (26): Audit Events, Blocker State Derivation Logic, Blocker State Handling, Data Flow, Database Changes, Frontend Integration Notes, Implementation Notes, Implemented Endpoints (+18 more)

### Community 39 - "Frontend Implementation Summary"
Cohesion: 0.07
Nodes (26): Accessibility, API Client, Authentication, Backend Integration, Browser Compatibility, Build Output, Code Quality, Completed Features (+18 more)

### Community 40 - "AlertQueueViewModelTest"
Cohesion: 0.19
Nodes (3): Alert, AlertQueueUiState, AlertQueueViewModelTest

### Community 41 - "conftest.py"
Cohesion: 0.20
Nodes (3): client(), db_session(), _fresh_schema()

### Community 42 - "requests.py"
Cohesion: 0.17
Nodes (6): create_information_request(), get_information_request(), record_information_response(), InformationRequestDetail, RecordResponseRequest, RecordResponseResponse

### Community 44 - "TASK-4 Handoff: Transaction Evidence and Case Creation"
Cohesion: 0.22
Nodes (8): Completed Endpoints, Database Schema, Flows, GET /api/v1/alerts/{alertId}/evidence, POST /api/v1/cases, Seed Data, TASK-4 Handoff: Transaction Evidence and Case Creation, Technical Notes

### Community 45 - "AML Transaction Monitoring Workbench - Frontend"
Cohesion: 0.07
Nodes (29): AML Transaction Monitoring Workbench - Frontend, API Integration, Authentication, Browser Support, Build for Production, Configuration, Deployment, Design System (+21 more)

### Community 46 - "User"
Cohesion: 0.09
Nodes (15): hash_password(), User, seed_users(), auth_client(), test_assign_alert_not_found(), investigator_user(), officer_user(), test_login_endpoint() (+7 more)

### Community 47 - "TASK-5: Backend Feature B3 - Historical Rule Snapshots and Linked Alerts"
Cohesion: 0.09
Nodes (21): 1. Rule Evaluation Snapshots, 3. Link Additional Alerts Endpoint, 4. Database Migration, 5. Seed Data, API Endpoints, Cases with Linked Alerts, Compliance & Requirements, Example Flows (+13 more)

### Community 48 - "EvidenceGap"
Cohesion: 0.18
Nodes (6): EvidenceGap, test_open_request_blocks_decision(), test_overdue_request_blocks_decision(), test_readiness_shows_incomplete_when_open_requests_exist(), test_responding_to_request_clears_blocker(), Models

### Community 49 - "cases.py"
Cohesion: 0.05
Nodes (25): RuleSnapshotRepository, add_note(), get_alert_evidence(), get_case_workspace(), link_alert_to_case(), LinkAlertRequest, LinkAlertResponse, AddNoteRequest (+17 more)

### Community 51 - "with"
Cohesion: 0.06
Nodes (46): defaults, name, runs-on, steps, run, name, needs, runs-on (+38 more)

### Community 53 - "decision_service.py"
Cohesion: 0.06
Nodes (15): DecisionRepository, assign_officer(), get_officer_review(), record_decision(), share_for_review(), AssignOfficerRequest, AssignOfficerResponse, DecisionResponse (+7 more)

### Community 54 - "Frontend Navigation Structure"
Cohesion: 0.15
Nodes (12): Alerts Section (`/alerts`), AppLayout Component (`src/components/AppLayout.tsx`), Between Sections, Cases Section (`/cases`), From Alerts to Cases, Frontend Navigation Structure, Implementation Details, Navigation Flow (+4 more)

### Community 55 - "Development Workflow"
Cohesion: 0.18
Nodes (11): 10. Lint, 1. Create Feature Branch, 2. Make Changes, 3. Create Migration, 4. Review and Edit Migration, 5. Apply Migration, 6. Update Seed Data (if needed), 7. Write Tests (+3 more)

### Community 57 - "TASK-7 Backend Handoff: Evidence Gap Tracking and Information Request Creation"
Cohesion: 0.12
Nodes (16): API Endpoints, Blocker State Management, Create Information Request Flow, Database Schema, evidence_gaps, Evidence Gaps, Frontend Integration Notes, information_requests (+8 more)

### Community 60 - "Key Navigation Elements"
Cohesion: 0.20
Nodes (9): Create and Investigate a Case, Key Navigation Elements, Navigation Diagram, Navigation States, Page-Level Navigation, Resolve an Information Request, Top-Level Tabs (Always Visible When Authenticated), User Journey Examples (+1 more)

### Community 65 - "test_audit_trail_integration.py"
Cohesion: 0.14
Nodes (6): test_alert_assignment_creates_audit_event(), test_audit_trail_provides_complete_case_history(), test_case_creation_creates_audit_events(), test_decision_recording_creates_audit_event(), test_note_capture_creates_audit_event(), test_officer_assignment_creates_audit_event()

### Community 68 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 69 - "api.ts"
Cohesion: 0.07
Nodes (27): AccountContext, AddNoteRequest, AddNoteResponse, AlertAssignmentResponse, AlertEvidenceResponse, AlertQueueResponse, ApiError, AssignOfficerRequest (+19 more)

### Community 70 - "test_case_service.py"
Cohesion: 0.05
Nodes (14): AuditEvent, CaseRepository, create_case(), get_case_readiness(), EligibleOfficer, PackageSummary, ReadinessChecklistItem, ReadinessProjection (+6 more)

### Community 71 - "OfficerReviewPage.tsx"
Cohesion: 0.23
Nodes (7): apiClient, DecisionOutcome, RequestResolutionPage(), AlertQueueItem, InformationRequestDetail, OfficerReviewPackage, ReadinessProjection

### Community 72 - "routers/auth.py"
Cohesion: 0.16
Nodes (7): get_me(), login(), ErrorResponse, LoginRequest, LoginResponse, LogoutResponse, UserResponse

### Community 73 - "Alerts Feature Module"
Cohesion: 0.14
Nodes (13): Alerts Feature Module, API Integration, Backend Integration, ✅ Completed Components, Design Fidelity, Environment Constraints, File Structure, Implementation Gaps (+5 more)

### Community 74 - "AlertEvidence"
Cohesion: 0.36
Nodes (7): toDomain(), AccountContext, AlertEvidence, CustomerContext, RuleEvaluationSnapshot, TransactionFacts, EvidenceUiState

### Community 75 - "App.tsx"
Cohesion: 0.26
Nodes (13): App(), AppLayout(), AppLayoutProps, AlertEvidencePage(), AlertQueuePage(), CaseListItem, CasesPage(), LoginPage() (+5 more)

### Community 76 - "AlertDto.kt"
Cohesion: 0.16
Nodes (11): AmlApiService, AccountContextDto, AlertAssignmentResponse, AlertEvidenceDto, AlertQueueItemDto, AlertQueueResponse, CreateCaseRequest, CreateCaseResponse (+3 more)

### Community 79 - "package.json"
Cohesion: 0.22
Nodes (9): devDependencies, @playwright/test@^1.40.1, @playwright/test, name, private, scripts, test:e2e, test:e2e:ui (+1 more)

### Community 80 - "AlertQueueEvent"
Cohesion: 0.22
Nodes (9): AlertQueueEvent, AssignAlert, ClearAssignmentFeedback, FilterByOwnership, FilterByPriority, FilterByStatus, LoadNextPage, Refresh (+1 more)

### Community 81 - "compilerOptions"
Cohesion: 0.25
Nodes (7): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, skipLibCheck, include

### Community 82 - "EvidenceEvent"
Cohesion: 0.50
Nodes (4): ClearCaseCreationFeedback, CreateCase, EvidenceEvent, Retry

### Community 83 - "alerts.py"
Cohesion: 0.15
Nodes (7): get_db(), assign_alert(), get_alert_queue(), AlertAssignmentRequest, AlertAssignmentResponse, AlertQueueResponse, ErrorResponse

### Community 84 - "dependencies"
Cohesion: 0.22
Nodes (9): dependencies, react@^18.2.0, react-dom@^18.2.0, react-router-dom@^6.20.1, zustand@^4.4.7, AuthState, User, react-dom (+1 more)

### Community 85 - "ReadinessRepository"
Cohesion: 0.14
Nodes (5): ReadinessRepository, test_check_conflicted_officer(), test_derive_blocker_state_none(), test_derive_blocker_state_open_requests(), test_derive_blocker_state_overdue_requests()

### Community 87 - "API Routes"
Cohesion: 0.22
Nodes (9): Alerts (`/api/v1/alerts/`), API Routes, Authentication (`/api/v1/auth/`), Cases (`/api/v1/cases/`), Decisions (`/api/v1/cases/{caseId}/`), Evidence (`/api/v1/alerts/`), Health, Information Requests (`/api/v1/cases/{caseId}/requests/`) (+1 more)

### Community 88 - "CaseInvestigationPage.tsx"
Cohesion: 0.33
Nodes (5): CaseInvestigationPage(), NoteCategory, TabType, CaseNote, CaseWorkspaceResponse

### Community 89 - "Database Migrations"
Cohesion: 0.29
Nodes (7): Apply All Migrations, Check Current Version, Create New Migration, Database Migrations, Review Generated Migration, Rollback Last Migration, View Migration History

### Community 105 - "main.py"
Cohesion: 0.16
Nodes (4): init_db(), health_check(), lifespan(), root()

### Community 106 - "test_four_eyes_integration.py"
Cohesion: 0.12
Nodes (8): investigator_user(), officer_user(), test_four_eyes_allows_independent_officer_assignment(), test_four_eyes_eligible_officers_excludes_case_creator(), test_four_eyes_independent_officer_can_review_and_decide(), test_four_eyes_prevents_conflicted_officer_decision(), test_four_eyes_prevents_conflicted_officer_from_reviewing(), test_four_eyes_prevents_self_assignment_as_officer()

### Community 107 - "Security"
Cohesion: 0.29
Nodes (7): Audit Trail, Decision Blockers, Four-Eyes Enforcement, JWT Tokens, Password Security, Security, Session Management

### Community 108 - "test_full_flow_integration.py"
Cohesion: 0.15
Nodes (5): investigator_user(), officer_user(), test_alert_queue_pagination_and_filtering(), test_full_investigator_to_officer_flow(), test_derive_checklist_case_not_found()

### Community 109 - "test_pipeline_migration_parity.py"
Cohesion: 0.33
Nodes (6): _alembic(), _env_py_text(), _has_alembic_version(), migrated(), test_migrations_match_the_models(), test_uuid_columns_are_stored_as_text()

### Community 110 - "_mapped_columns"
Cohesion: 0.31
Nodes (6): _annotation_kind(), _column_kind(), _foreign_key(), _last_name(), _mapped_columns(), test_uuid_ids_have_one_type_end_to_end()

### Community 112 - "middleware/auth.py"
Cohesion: 0.18
Nodes (3): get_current_active_user(), get_current_user(), require_role()

### Community 113 - "information_request_service.py"
Cohesion: 0.19
Nodes (3): InformationRequestService, test_record_response(), test_record_response_not_found()

### Community 114 - "Testing"
Cohesion: 0.33
Nodes (6): Run All Tests, Run Specific Test File, Run Tests Matching Pattern, Run Tests with Coverage, Test Categories, Testing

### Community 117 - "Troubleshooting"
Cohesion: 0.40
Nodes (5): Database Connection Issues, Import Errors, Migration Issues, Test Failures, Troubleshooting

### Community 118 - "Database Schema"
Cohesion: 0.50
Nodes (4): Additional Tables, Core Tables, Database Schema, Domain Tables

### Community 119 - "Dependencies"
Cohesion: 0.50
Nodes (4): Core Dependencies, Dependencies, Development Dependencies, Optional Dependencies

### Community 120 - "Installation"
Cohesion: 0.50
Nodes (4): Development Dependencies, Installation, PostgreSQL Support, Standard Installation (SQLite)

### Community 123 - "Code Quality"
Cohesion: 0.67
Nodes (3): Auto-fix Issues, Code Quality, Linting with Ruff

## Knowledge Gaps
- **11 isolated node(s):** `DATABASE_URL`, `AssignAlert`, `ClearAssignmentFeedback`, `FilterByOwnership`, `FilterByPriority` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 955 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **52 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `AmlCase`, `Session`, `security.py`, `test_case_service.py`, `routers/auth.py`, `conftest.py`, `requests.py`, `test_four_eyes_integration.py`, `test_full_flow_integration.py`, `middleware/auth.py`, `cases.py`, `alerts.py`, `ReadinessRepository`, `decision_service.py`, `test_alert_service.py`, `seed.py`, `Alert`, `UUID`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `User` (e.g. with `get_current_active_user()` and `get_current_user()`) actually correct?**
  _`User` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `DATABASE_URL`, `AssignAlert`, `ClearAssignmentFeedback` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AML Transaction Monitoring & Compliance Workbench` be split into smaller, more focused modules?**
  _Cohesion score 0.043478260869565216 - nodes in this community are weakly interconnected._
- **Why does `Alert` connect `AlertQueueViewModelTest` to `AlertEvidence`, `EvidenceViewModelTest.kt`, `EvidenceScreen.kt`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Session` (e.g. with `AuthService` and `test_login_success()`) actually correct?**
  _`Session` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `AmlCase` be split into smaller, more focused modules?**
  _Cohesion score 0.11384615384615385 - nodes in this community are weakly interconnected._