# AML Transaction Monitoring & Compliance Workbench

A compliance-first investigation product for reviewing suspicious transaction alerts, consolidating supporting evidence, managing evidence gaps, and recording independently reviewed final dispositions. The system enables AML investigators and independent compliance officers to move from suspicious transaction alert to defensible case outcome in one continuous workflow.

## Product Overview

The AML Workbench implements a complete six-screen investigation workflow:

1. **Alert Queue** - Prioritize and assign high-risk alerts with filtering and search
2. **Alert Evidence** - Review transaction facts and immutable historical rule snapshots
3. **Case Investigation** - Create cases, add notes, link alerts, identify evidence gaps
4. **Information Requests** - Issue requests, record responses, resolve blockers
5. **Readiness Review** - Verify checklist and assign independent officer
6. **Officer Decision** - Independent review and final decision with mandatory rationale

### Core Compliance Controls

- **Four-Eyes Segregation**: Case creator cannot be the deciding officer (backend enforced)
- **Immutable Audit Trail**: All actions captured with actor, timestamp, and correlation ID
- **Decision Blockers**: Prevent final decisions while information requests are open/overdue
- **Historical Rule Snapshots**: Preserve exact rule versions used at alert generation
- **Mandatory Rationale**: Officer decisions require explicit rationale text

## Technology Stack

- **Frontend**: React 18 + TypeScript + Vite (Material Design 3 semantics)
- **Backend**: Python 3.11+ with FastAPI, SQLAlchemy, Alembic migrations
- **Database**: SQLite for local development, PostgreSQL for production
- **Authentication**: JWT tokens with bcrypt password hashing and server-side session tracking
- **Testing**: pytest (backend), vitest (frontend), Playwright (end-to-end)

## Prerequisites

- **Python 3.11+** - [Download](https://python.org)
- **Node.js 20.19+** - [Download](https://nodejs.org) (required by Vite 8)
- **Git** - [Download](https://git-scm.com)

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd aml-transaction-monitoring
```

### 2. Start all services

```bash
./start.sh
```

**Windows users**: Run `start.bat` which executes `start.sh` under Git Bash

The startup script will:
- Check prerequisites (Python 3.11+, Node.js 20.19+)
- Create Python virtual environment (`.venv`)
- Install backend dependencies
- Copy `dev.env` to `.env` if needed
- Run database migrations (`alembic upgrade head`)
- Seed default users
- Start backend API server (port 9000+)
- Install frontend dependencies
- Start frontend dev server (port 5173+)

**Default Ports:**
- Backend API: http://localhost:9000 (or next available)
- API Documentation: http://localhost:9000/api/v1/docs
- Health Check: http://localhost:9000/health
- Frontend: http://localhost:5173 (or next available)

### 3. Login with seed credentials

| Role          | Email                         | Password         |
|---------------|-------------------------------|------------------|
| Investigator  | investigator@example.com      | investigator123  |
| Officer       | officer@example.com           | officer123       |
| Auditor       | auditor@example.com           | auditor123       |
| Supervisor    | supervisor@example.com        | supervisor123    |

### 4. Stop all services

```bash
./stop.sh
```

**Windows users**: Run `stop.bat`

## Architecture

### System Design

The AML Workbench is a modular monolith with clear internal service boundaries:

- **Frontend**: Single-page React application with Material 3 design system
- **Backend**: FastAPI modular monolith with domain-separated services
- **Database**: Relational schema with immutable audit records

### Directory Structure

```
aml-transaction-monitoring/
├── frontend/                     # React + TypeScript frontend
│   ├── src/
│   │   ├── api/                 # API client with JWT auth
│   │   ├── pages/               # Screen components (6 screens)
│   │   ├── stores/              # Zustand state management
│   │   ├── styles/              # Design system CSS (Material 3)
│   │   └── types/               # TypeScript type definitions
│   ├── package.json
│   └── vite.config.ts
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── seed.py              # Database seeding
│   │   ├── core/                # Security utilities
│   │   ├── models/              # SQLAlchemy ORM models (16 tables)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── repositories/        # Data access layer
│   │   ├── services/            # Business logic layer
│   │   ├── routers/             # API route handlers
│   │   └── middleware/          # Auth middleware
│   ├── alembic/                 # Database migrations (7 revisions)
│   ├── tests/                   # Test suite (73+ tests)
│   ├── pyproject.toml           # Python dependencies
│   ├── dev.env                  # Development environment (committed)
│   └── .env.example             # Environment template
├── e2e/                          # Playwright end-to-end tests
│   ├── journey_full_flow.spec.ts
│   └── journey_blocked_decision.spec.ts
├── android/                      # Android design system reference
│   ├── core/designsystem/       # Material 3 design tokens (Kotlin)
│   └── README.md                # Design system documentation
├── .github/workflows/
│   └── ci.yml                   # GitHub Actions CI pipeline
├── start.sh                     # Startup script (cross-platform)
├── stop.sh                      # Shutdown script
├── start.bat                    # Windows wrapper for start.sh
├── stop.bat                     # Windows wrapper for stop.sh
└── README.md                    # This file
```

### Backend Architecture

**Layered Structure:**
- **Routers** → Define API endpoints and request/response contracts
- **Services** → Implement business logic and compliance controls
- **Repositories** → Handle database queries and data access
- **Models** → SQLAlchemy ORM models for 16 domain tables

**Key Services:**
- Authentication & Session Management
- Alert Triage (queue, filters, assignment)
- Evidence & Rule Snapshot Retrieval
- Case Management (creation, notes, linked alerts)
- Information Request Lifecycle
- Readiness & Officer Assignment
- Decision Recording with Immutability
- Audit Event Capture

### Frontend Architecture

**Design System:**
- Material 3 color scheme and typography
- 4dp baseline spacing grid
- Compliance-specific components (blocker banners, readiness checklist, decision selector)

**State Management:**
- Zustand stores for auth state
- React Query for API data
- Form state with validation

**Routing:**
- `/alerts` - Alert queue
- `/alerts/:id/evidence` - Evidence review
- `/cases` - Cases list
- `/cases/:id/investigation` - Case workspace
- `/cases/:id/requests/:id` - Request resolution
- `/cases/:id/readiness` - Readiness review
- `/cases/:id/officer-review` - Officer decision

## Development

### Backend Development

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install .

# Run tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ -v --cov=app --cov-report=html

# Type checking
python -m mypy app --check-untyped-defs --ignore-missing-imports

# Create migration
python -m alembic revision --autogenerate -m "description"

# Apply migrations
python -m alembic upgrade head

# Seed database
python app/seed.py
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Run unit tests
npm test

# Type check
npx tsc --noEmit

# Lint
npm run lint

# Build for production
npm run build
```

### End-to-End Testing

```bash
# Install Playwright
npx playwright install --with-deps chromium

# Run e2e tests (requires backend + frontend running)
npx playwright test

# Run specific journey
npx playwright test e2e/journey_full_flow.spec.ts

# Debug mode
npx playwright test --debug
```

## Environment Configuration

### Backend Configuration

Copy `backend/dev.env` to `backend/.env` and customize:

```bash
# Database - SQLite for local, PostgreSQL for production
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

**PostgreSQL Example:**

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/aml_workbench
```

**Required Environment Variables:**
- `SECRET_KEY` - Must be at least 32 characters for production
- `DATABASE_URL` - Database connection string

**Optional Environment Variables:**
- `JWT_ALGORITHM` - Default: HS256
- `JWT_EXPIRY_MINUTES` - Default: 480 (8 hours)
- `CORS_ORIGINS` - Default: http://localhost:5173
- `RATE_LIMIT_ENABLED` - Default: true
- `DEBUG` - Default: false

### Frontend Configuration

The frontend uses Vite's proxy for same-origin API access:

```typescript
// vite.config.ts proxy configuration
server: {
  proxy: {
    '/api': {
      target: `http://localhost:${process.env.BACKEND_PORT || 9000}`,
      changeOrigin: true,
    }
  }
}
```

**No environment variables needed** - frontend calls relative `/api` paths which are proxied to backend.

## API Documentation

### OpenAPI Documentation

Once the backend is running:
- **Swagger UI**: http://localhost:9000/api/v1/docs
- **ReDoc**: http://localhost:9000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:9000/api/v1/openapi.json

### Key API Endpoints

**Authentication:**
- `POST /api/v1/auth/login` - Login (returns JWT token)
- `POST /api/v1/auth/logout` - Logout (revoke session)
- `GET /api/v1/auth/me` - Get current user

**Alerts:**
- `GET /api/v1/alerts` - Get alert queue (with filters)
- `POST /api/v1/alerts/{id}/assign` - Assign alert to self

**Cases:**
- `POST /api/v1/cases` - Create case from alert
- `GET /api/v1/cases/{id}/workspace` - Get case workspace
- `POST /api/v1/cases/{id}/notes` - Add investigation note
- `POST /api/v1/cases/{id}/link-alert` - Link alert to case

**Evidence:**
- `GET /api/v1/alerts/{id}/evidence` - Get alert evidence with rule snapshots

**Information Requests:**
- `POST /api/v1/cases/{id}/requests` - Create information request
- `GET /api/v1/cases/{id}/requests/{reqId}` - Get request details
- `POST /api/v1/cases/{id}/requests/{reqId}/response` - Record response

**Readiness & Decision:**
- `GET /api/v1/cases/{id}/readiness` - Get readiness checklist
- `POST /api/v1/cases/{id}/assign-officer` - Assign independent officer
- `POST /api/v1/cases/{id}/share-for-review` - Share for officer review
- `GET /api/v1/cases/{id}/officer-review` - Get officer review package
- `POST /api/v1/cases/{id}/decision` - Record final decision

**Health:**
- `GET /health` - Health check

## Database Schema

The backend uses 16 domain tables:

| Table                        | Purpose                                      |
|------------------------------|----------------------------------------------|
| users                        | User accounts with role-based access         |
| sessions                     | Server-side JWT session tracking             |
| customers                    | Customer master data                         |
| accounts                     | Account information                          |
| transactions                 | Transaction records                          |
| alerts                       | Suspicious transaction alerts                |
| aml_cases                    | Investigation cases                          |
| case_alert_links             | Alert-to-case linkage (with primary flag)    |
| case_notes                   | Investigation narrative                      |
| evidence_gaps                | Identified missing evidence                  |
| information_requests         | Evidence requests with lifecycle tracking    |
| request_attachments          | Attachment metadata                          |
| rule_evaluation_snapshots    | Immutable historical rule evaluations        |
| case_review_assignments      | Independent officer assignments              |
| case_decisions               | Immutable final decisions with rationale     |
| audit_events                 | Complete audit trail                         |

**See `backend/README.md` for detailed schema documentation.**

## Testing

### Backend Tests (73+ tests)

```bash
cd backend
python -m pytest tests/ -v
```

**Test Coverage:**
- Authentication & Authorization (17 tests)
- Alert Service (7 tests)
- Alert Integration (9 tests)
- Evidence Service (2 tests)
- Case Service (4 tests)
- Case Workspace (2 tests)
- Case Notes (2 tests)
- Information Requests (3 tests)
- Rule Snapshots (2 tests)
- Readiness Service (3 tests)
- Decision Service (3 tests)
- Four-Eyes Enforcement (3 tests)
- Decision Immutability (2 tests)
- Officer Review (5 tests)
- Blocker Enforcement (3 tests)
- Audit Trail Integration (5 tests)
- Migration Parity (4 tests)
- Seed Execution (2 tests)

### Frontend Tests

```bash
cd frontend
CI=true npm test
```

### End-to-End Tests

```bash
npx playwright test
```

**Journey Tests:**
- Full investigation workflow (investigator → officer decision)
- Blocked decision workflow (open request prevents decision)

### CI Pipeline

GitHub Actions runs on every push/PR:
1. Backend tests (pytest with coverage, mypy type checking)
2. Frontend tests (TypeScript typecheck, unit tests, build)
3. End-to-end tests (Playwright with backend + frontend servers)
4. Lint checks (ruff for Python, ESLint for TypeScript)

## Deployment

### Docker Deployment

Build and run with Docker Compose:

```bash
docker-compose up --build
```

The application will be available at http://localhost:80

### Production Considerations

1. **Database**: Use PostgreSQL for production
2. **Secret Key**: Generate a secure 32+ character secret
3. **CORS**: Configure allowed origins
4. **TLS**: Enable HTTPS
5. **Environment Variables**: Never commit production secrets

## Security

### Password Security
- Bcrypt hashing (cost factor 12)
- Minimum 8 characters enforced
- No plaintext storage or logging

### JWT Tokens
- HS256 algorithm
- Include user ID, role, expiry, correlation ID
- 8-hour default expiry (configurable)
- Server-side session tracking for revocation

### Session Management
- Token hash stored server-side (SHA-256)
- Automatic cleanup of expired sessions
- Activity tracking

### CORS Configuration
- Explicit origin whitelist (no wildcards)
- Configurable via environment

### Compliance Controls
- Four-eyes enforcement (backend validated)
- Decision blockers (backend enforced)
- Immutable audit records
- Role-based access control

## Troubleshooting

### Common Issues

**Port already in use:**
- The startup script automatically finds the next available port
- Check `.pids` file and run `./stop.sh` to clean up

**Database migration failed:**
```bash
cd backend
rm app.db  # Only for local SQLite
python -m alembic upgrade head
```

**Module not found:**
```bash
cd backend
source .venv/bin/activate
pip install .
```

**Frontend build errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Git Bash not found (Windows):**
- Install [Git for Windows](https://git-scm.com/download/win)
- Restart terminal and run `start.bat`

## License

Apache License 2.0

## Stack Deviation Note

**Important**: The design documents (`design.md`, `android/` directory) specify Android/Kotlin/Jetpack Compose. However, this implementation uses **React + TypeScript + Vite** for the frontend as required by the build pipeline constraints.

The Android design system artifacts in `android/core/designsystem/` document the Material 3 design tokens, color schemes, typography, and component specifications. These design semantics (Material 3 patterns, edge-to-edge behavior, accessibility requirements, compliance-specific components) are **preserved as specifications** that have been adapted to the web implementation.

**See `STACK_DEVIATION.md` for complete rationale.**

## Additional Documentation

- **Backend API**: See `backend/README.md`
- **Android Design System**: See `android/README.md`
- **CI/CD**: See `.github/workflows/ci.yml`
- **Architecture**: See `artifacts/b63badc6df75_plan/hld/HLD_Document.md`
