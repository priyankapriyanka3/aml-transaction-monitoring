# AML Workbench Backend

FastAPI backend for the AML Transaction Monitoring & Compliance Workbench.

## Quick Start

From the repository root:

```bash
./start.sh
```

Or run directly from backend directory:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install .
cp dev.env .env  # if .env doesn't exist
python -m alembic upgrade head
python app/seed.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Environment configuration (pydantic-settings)
│   ├── database.py              # SQLAlchemy engine and session setup
│   ├── seed.py                  # Database seeding with default users
│   ├── core/
│   │   └── security.py          # Password hashing, JWT tokens, token hashing
│   ├── models/                  # SQLAlchemy ORM models (16 tables)
│   │   ├── __init__.py          # Model registry
│   │   ├── user.py              # User accounts with roles
│   │   ├── session.py           # Server-side session tracking
│   │   ├── customer.py          # Customer master data
│   │   ├── account.py           # Account information
│   │   ├── transaction.py       # Transaction records
│   │   ├── alert.py             # Suspicious transaction alerts
│   │   ├── case.py              # Investigation cases
│   │   ├── case_alert_link.py   # Alert-to-case linkage
│   │   ├── case_note.py         # Investigation notes
│   │   ├── evidence_gap.py      # Evidence gaps
│   │   ├── information_request.py  # Information requests
│   │   ├── request_attachment.py   # Attachment metadata
│   │   ├── rule_snapshot.py     # Immutable rule evaluations
│   │   ├── case_review_assignment.py  # Officer assignments
│   │   ├── case_decision.py     # Final decisions
│   │   └── audit_event.py       # Audit trail
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── auth_schemas.py
│   │   ├── alert_schemas.py
│   │   ├── case_schemas.py
│   │   ├── evidence_schemas.py
│   │   ├── request_schemas.py
│   │   ├── readiness_schemas.py
│   │   └── decision_schemas.py
│   ├── repositories/            # Data access layer
│   │   ├── alert_repository.py
│   │   ├── case_repository.py
│   │   ├── information_request_repository.py
│   │   ├── readiness_repository.py
│   │   ├── decision_repository.py
│   │   └── rule_snapshot_repository.py
│   ├── services/                # Business logic layer
│   │   ├── auth_service.py      # Authentication and session management
│   │   ├── alert_service.py     # Alert queue and assignment
│   │   ├── evidence_service.py  # Evidence retrieval
│   │   ├── case_service.py      # Case management
│   │   ├── information_request_service.py  # Request lifecycle
│   │   ├── readiness_service.py # Readiness checklist
│   │   └── decision_service.py  # Officer decision with four-eyes
│   ├── routers/                 # API route handlers
│   │   ├── auth.py              # /api/v1/auth/*
│   │   ├── alerts.py            # /api/v1/alerts/*
│   │   ├── cases.py             # /api/v1/cases/*
│   │   ├── requests.py          # /api/v1/cases/{id}/requests/*
│   │   ├── readiness.py         # /api/v1/cases/{id}/readiness
│   │   └── decisions.py         # /api/v1/cases/{id}/decision
│   └── middleware/
│       └── auth.py              # JWT authentication middleware
├── alembic/                     # Database migrations
│   ├── versions/                # Migration scripts (7 revisions)
│   │   ├── 20261122_1400_001_create_users_sessions.py
│   │   ├── 20261122_1400_002_create_alert_tables.py
│   │   ├── 20261122_1400_003_create_case_tables.py
│   │   ├── 20261122_1400_004_create_rule_snapshots_table.py
│   │   ├── 20261122_1400_005_create_case_notes_table.py
│   │   ├── 20261122_1400_006_create_info_request_tables.py
│   │   └── 20261122_1400_007_create_assignment_decision_tables.py
│   └── env.py                   # Alembic environment configuration
├── tests/                       # Test suite (73+ tests)
│   ├── conftest.py              # Shared test fixtures
│   ├── test_auth_service.py     # Authentication tests (17)
│   ├── test_alert_service.py    # Alert service tests (7)
│   ├── test_alert_integration.py  # Alert integration tests (9)
│   ├── test_evidence_service.py   # Evidence tests (2)
│   ├── test_case_service.py     # Case service tests (4)
│   ├── test_case_workspace.py   # Workspace tests (2)
│   ├── test_case_note_service.py  # Note tests (2)
│   ├── test_information_request_service.py  # Request tests (3)
│   ├── test_rule_snapshot_service.py  # Snapshot tests (2)
│   ├── test_readiness_service.py  # Readiness tests (3)
│   ├── test_decision_service.py   # Decision tests (3)
│   ├── test_four_eyes_enforcement.py  # Four-eyes tests (3)
│   ├── test_decision_immutability.py  # Immutability tests (2)
│   ├── test_officer_review.py   # Review tests (5)
│   ├── test_blocker_enforcement.py  # Blocker tests (3)
│   ├── test_audit_trail_integration.py  # Audit tests (5)
│   ├── test_pipeline_migration_parity.py  # Migration tests (4)
│   └── test_pipeline_seed_runs.py  # Seed tests (2)
├── pyproject.toml               # Python dependencies
├── alembic.ini                  # Alembic configuration
├── dev.env                      # Development environment (committed)
├── .env.example                 # Environment template
└── README.md                    # This file
```

## Dependencies

### Core Dependencies

```toml
[project]
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "bcrypt>=4.1.2",
    "pyjwt>=2.8.0",
    "email-validator>=2.0.0",
    "python-multipart>=0.0.6",
]
```

### Optional Dependencies

```toml
[project.optional-dependencies]
postgres = [
    "psycopg[binary]>=3.2",
]
```

### Development Dependencies

```toml
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.7.0",
    "ruff>=0.1.0",
]
```

## Installation

### Standard Installation (SQLite)

```bash
pip install .
```

### PostgreSQL Support

```bash
pip install ".[postgres]"
```

### Development Dependencies

```bash
pip install ".[dev]"
```

## Environment Configuration

### Required Settings

Copy `dev.env` to `.env` and customize:

```bash
# Database Connection
DATABASE_URL=sqlite:///./app.db

# Security - REQUIRED, minimum 32 characters
SECRET_KEY=your-secret-key-at-least-32-characters-long

# JWT Configuration
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=480

# CORS - Comma-separated allowed origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Features
RATE_LIMIT_ENABLED=true
DEBUG=false
```

### Database URLs

**SQLite (Local Development):**
```bash
DATABASE_URL=sqlite:///./app.db
```

**PostgreSQL (Production):**
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/aml_workbench
```

## Database Migrations

### Apply All Migrations

```bash
python -m alembic upgrade head
```

### Create New Migration

After modifying models in `app/models/`:

```bash
python -m alembic revision --autogenerate -m "description of changes"
```

### Review Generated Migration

Always review auto-generated migrations in `alembic/versions/` before applying.

### Rollback Last Migration

```bash
python -m alembic downgrade -1
```

### Check Current Version

```bash
python -m alembic current
```

### View Migration History

```bash
python -m alembic history
```

## Database Seeding

### Seed Default Users

```bash
python app/seed.py
```

**Default Credentials:**

| Role          | Email                         | Password         |
|---------------|-------------------------------|------------------|
| Investigator  | investigator@example.com      | investigator123  |
| Officer       | officer@example.com           | officer123       |
| Auditor       | auditor@example.com           | auditor123       |
| Supervisor    | supervisor@example.com        | supervisor123    |

**Seed Data Includes:**
- 4 users (one per role)
- 10 customers
- 10 accounts
- 20 transactions
- 15 alerts (various priorities)
- 6 cases (various statuses)
- 17 rule evaluation snapshots
- 8 investigation notes
- 5 information requests
- 2 officer assignments
- 1 completed decision

### Idempotent Seeding

The seed script is idempotent - it can be run multiple times safely:
- Checks for existing users by email before creating
- Skips duplicate data
- Safe to run after schema changes

## API Routes

### Authentication (`/api/v1/auth/`)

| Method | Endpoint                  | Description                      |
|--------|---------------------------|----------------------------------|
| POST   | `/api/v1/auth/login`      | Login (returns JWT token)        |
| POST   | `/api/v1/auth/logout`     | Logout (revoke session)          |
| GET    | `/api/v1/auth/me`         | Get current user info            |

### Alerts (`/api/v1/alerts/`)

| Method | Endpoint                      | Description                           |
|--------|-------------------------------|---------------------------------------|
| GET    | `/api/v1/alerts`              | Get alert queue (with filters)        |
| POST   | `/api/v1/alerts/{id}/assign`  | Assign alert to current user          |

### Cases (`/api/v1/cases/`)

| Method | Endpoint                              | Description                      |
|--------|---------------------------------------|----------------------------------|
| POST   | `/api/v1/cases`                       | Create case from alert           |
| GET    | `/api/v1/cases/{id}/workspace`        | Get case workspace               |
| POST   | `/api/v1/cases/{id}/notes`            | Add investigation note           |
| POST   | `/api/v1/cases/{id}/link-alert`       | Link additional alert to case    |

### Evidence (`/api/v1/alerts/`)

| Method | Endpoint                          | Description                               |
|--------|-----------------------------------|-------------------------------------------|
| GET    | `/api/v1/alerts/{id}/evidence`    | Get evidence with rule snapshots          |

### Information Requests (`/api/v1/cases/{caseId}/requests/`)

| Method | Endpoint                                          | Description                      |
|--------|---------------------------------------------------|----------------------------------|
| POST   | `/api/v1/cases/{id}/requests`                     | Create information request       |
| GET    | `/api/v1/cases/{id}/requests/{reqId}`             | Get request details              |
| POST   | `/api/v1/cases/{id}/requests/{reqId}/response`    | Record request response          |

### Readiness (`/api/v1/cases/{caseId}/readiness`)

| Method | Endpoint                              | Description                               |
|--------|---------------------------------------|-------------------------------------------|
| GET    | `/api/v1/cases/{id}/readiness`        | Get readiness checklist and eligible officers |

### Decisions (`/api/v1/cases/{caseId}/`)

| Method | Endpoint                                  | Description                          |
|--------|-------------------------------------------|--------------------------------------|
| GET    | `/api/v1/cases/{id}/officer-review`       | Get officer review package           |
| POST   | `/api/v1/cases/{id}/assign-officer`       | Assign independent officer           |
| POST   | `/api/v1/cases/{id}/share-for-review`     | Share case for officer review        |
| POST   | `/api/v1/cases/{id}/decision`             | Record final decision                |

### Health

| Method | Endpoint   | Description        |
|--------|------------|--------------------|
| GET    | `/health`  | Health check       |

## Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test File

```bash
python -m pytest tests/test_auth_service.py -v
```

### Run Tests with Coverage

```bash
python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
```

View coverage report: `open htmlcov/index.html`

### Run Tests Matching Pattern

```bash
python -m pytest tests/ -k "auth" -v
```

### Test Categories

**Unit Tests:**
- Service layer tests
- Repository tests
- Security utility tests

**Integration Tests:**
- End-to-end API tests
- Multi-service workflow tests
- Database integration tests

**Pipeline Tests:**
- Migration parity verification
- Seed execution validation

## Type Checking

```bash
python -m mypy app --check-untyped-defs --ignore-missing-imports
```

### Type Check Specific Module

```bash
python -m mypy app/services/decision_service.py --ignore-missing-imports
```

## Code Quality

### Linting with Ruff

```bash
python -m ruff check app/ tests/
```

### Auto-fix Issues

```bash
python -m ruff check app/ tests/ --fix
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

Edit models, services, routers as needed.

### 3. Create Migration

```bash
python -m alembic revision --autogenerate -m "add new feature tables"
```

### 4. Review and Edit Migration

Check `alembic/versions/` for the generated migration file.

### 5. Apply Migration

```bash
python -m alembic upgrade head
```

### 6. Update Seed Data (if needed)

Edit `app/seed.py` to include test data for new features.

### 7. Write Tests

Add tests in `tests/` following existing patterns.

### 8. Run Tests

```bash
python -m pytest tests/ -v --cov=app
```

### 9. Type Check

```bash
python -m mypy app --check-untyped-defs --ignore-missing-imports
```

### 10. Lint

```bash
python -m ruff check app/ tests/
```

## API Documentation

When the backend is running:

- **Swagger UI**: http://localhost:9000/api/v1/docs
- **ReDoc**: http://localhost:9000/api/v1/redoc  
- **OpenAPI JSON**: http://localhost:9000/api/v1/openapi.json

## Database Schema

### Core Tables

**users** - User accounts with role-based access
- `user_id` (UUID, PK)
- `display_name` (VARCHAR 120)
- `email` (VARCHAR 255, UNIQUE)
- `hashed_password` (VARCHAR 255)
- `role` (VARCHAR 32) - INVESTIGATOR | OFFICER | AUDITOR | SUPERVISOR
- `is_active` (BOOLEAN)
- Timestamps: `created_at_utc`, `updated_at_utc`

**sessions** - Server-side session tracking
- `session_id` (UUID, PK)
- `user_id` (UUID, FK → users)
- `hashed_token` (VARCHAR 64) - SHA-256 hash
- Timestamps: `issued_at_utc`, `expires_at_utc`, `last_activity_utc`

### Domain Tables

**alerts** - Suspicious transaction alerts
- `alert_id` (UUID, PK)
- `alert_ref` (VARCHAR 32, UNIQUE)
- `transaction_id` (UUID, FK → transactions)
- `customer_id` (UUID, FK → customers)
- `priority` (VARCHAR 16) - Critical | High | Medium | Low
- `risk_score` (DECIMAL)
- `status` (VARCHAR 32)
- `owner_user_id` (UUID, FK → users, nullable)
- Timestamps: `triggered_at_utc`, `created_at_utc`

**aml_cases** - Investigation cases
- `case_id` (UUID, PK)
- `case_ref` (VARCHAR 32, UNIQUE) - Sequential CS-NNN
- `primary_alert_id` (UUID, FK → alerts)
- `created_by_user_id` (UUID, FK → users)
- `assigned_officer_user_id` (UUID, FK → users, nullable)
- `status` (VARCHAR 32) - OPEN | INVESTIGATING | PENDING_INFORMATION | UNDER_REVIEW | APPROVED | REJECTED | CLOSED
- `current_blocker_state` (VARCHAR 32) - NONE | OPEN_REQUESTS | OVERDUE_REQUESTS
- Timestamps: `created_at_utc`, `updated_at_utc`

**rule_evaluation_snapshots** - Immutable historical rule evaluations
- `snapshot_id` (UUID, PK)
- `alert_id` (UUID, FK → alerts)
- `rule_code` (VARCHAR 64)
- `rule_name` (VARCHAR 255)
- `rule_version` (VARCHAR 32)
- `outcome` (VARCHAR 16) - MATCH | PASS
- `condition_text` (TEXT)
- `immutable_hash` (VARCHAR 64) - SHA-256
- Timestamps: `evaluated_from_utc`, `evaluated_to_utc`, `created_at_utc`

**case_decisions** - Final immutable decisions
- `decision_id` (UUID, PK)
- `case_id` (UUID, FK → aml_cases, UNIQUE)
- `deciding_officer_user_id` (UUID, FK → users)
- `outcome` (VARCHAR 32) - APPROVED | REJECTED | ESCALATED | FALSE_POSITIVE
- `rationale_text` (TEXT, NOT NULL)
- `immutable_hash` (VARCHAR 64) - SHA-256
- Timestamp: `recorded_at_utc`

**audit_events** - Complete audit trail
- `audit_event_id` (UUID, PK)
- `entity_type` (VARCHAR 64)
- `entity_id` (UUID)
- `action_type` (VARCHAR 64)
- `actor_user_id` (UUID, FK → users)
- `actor_role` (VARCHAR 32)
- `correlation_id` (UUID)
- `details_json` (TEXT)
- Timestamp: `occurred_at_utc`

### Additional Tables

- `customers` - Customer master data
- `accounts` - Account information
- `transactions` - Transaction records
- `case_alert_links` - Alert-to-case linkage with `is_primary` flag
- `case_notes` - Investigation notes with category
- `evidence_gaps` - Identified missing evidence
- `information_requests` - Evidence requests with lifecycle
- `request_attachments` - Attachment metadata
- `case_review_assignments` - Independent officer assignments

## Security

### Password Security
- Bcrypt hashing with cost factor 12
- Minimum 8 characters enforced
- No plaintext storage or logging

### JWT Tokens
- HS256 algorithm
- Payload includes: user_id, role, iat, exp, correlation_id
- 8-hour default expiry (configurable)
- Server-side session tracking for revocation

### Session Management
- SHA-256 hash of token stored server-side
- Automatic cleanup of expired sessions
- Activity timestamp tracking

### Four-Eyes Enforcement
- Backend validation prevents case creator from being deciding officer
- Enforced at assignment, share-for-review, and decision recording

### Decision Blockers
- Backend rejects decisions while open/overdue requests exist
- Cannot be bypassed through UI

### Audit Trail
- All state-changing operations logged
- Immutable audit records
- Includes actor, role, timestamp, correlation ID

## Troubleshooting

### Database Connection Issues

```bash
# Check current DATABASE_URL
echo $DATABASE_URL

# Verify database file exists (SQLite)
ls -la app.db

# Test connection
python -c "from app.database import engine; print(engine.url)"
```

### Migration Issues

```bash
# Check current migration version
python -m alembic current

# View migration history
python -m alembic history

# Reset to specific version
python -m alembic downgrade <revision>

# Fresh start (SQLite only - destroys data)
rm app.db
python -m alembic upgrade head
```

### Import Errors

```bash
# Ensure virtual environment is activated
which python  # Should point to .venv

# Reinstall dependencies
pip install --force-reinstall .
```

### Test Failures

```bash
# Run with verbose output
python -m pytest tests/ -vv

# Run specific failing test
python -m pytest tests/test_auth_service.py::test_login_success -vv

# Check test database
DATABASE_URL=sqlite:///./test.db python -m pytest tests/ -v
```

## License

Apache License 2.0
