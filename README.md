# AML Transaction Monitoring & Compliance Workbench

Production-ready AML (Anti-Money Laundering) transaction monitoring and compliance investigation platform implementing alert queue management, case investigation workflows, information request tracking, and four-eyes review handoff.

## Architecture

- **Backend**: FastAPI (Python 3.11+) with SQLAlchemy 2.0
- **Frontend**: React 18 + TypeScript + Vite with Material 3 design system
- **Database**: SQLite locally, PostgreSQL in deployed environments
- **Migrations**: Alembic for schema management
- **API**: RESTful JSON API under `/api/v1`

## Quick Start

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 20.19+ or 22.12+
- **npm**: Latest version
- **Git**: For Windows users, Git Bash is required for running startup scripts

### One-Command Startup

The application includes cross-platform startup scripts that automatically set up and run both backend and frontend:

**Linux / macOS:**
```bash
./start.sh
```

**Windows:**
```batch
start.bat
```

The startup script will:
1. Check prerequisites (Python, Node.js, npm versions)
2. Stop any previous run
3. Create Python virtual environment if missing
4. Install backend dependencies
5. Copy `dev.env` to `.env` if needed
6. Run database migrations
7. Seed the database with sample data
8. Find available ports (starting from 9000 for backend, 5173 for frontend)
9. Update CORS configuration with selected frontend port
10. Start both backend and frontend servers
11. Display access URLs and default credentials

Once running, open **http://localhost:5173** in your browser.

### Default Credentials

The seed data includes two user accounts for testing:

**Investigator:**
- Username: `riya`
- Password: `password123`

**Compliance Officer:**
- Username: `morgan`
- Password: `password123`

### Stopping Services

To stop all running services:

**Linux / macOS:**
```bash
./stop.sh
```

**Windows:**
```batch
stop.bat
```

## Project Structure

```
aml-transaction-monitoring/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models (15 tables)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── repositories/    # Data access layer
│   │   ├── services/        # Business logic layer
│   │   ├── routers/         # FastAPI route handlers
│   │   ├── middleware/      # Auth, error handling, CORS
│   │   ├── config.py        # Environment-driven settings
│   │   ├── database.py      # Engine, session factory, Base
│   │   ├── main.py          # FastAPI app entrypoint
│   │   └── seed.py          # Database seed script
│   ├── alembic/             # Database migrations
│   ├── tests/               # Backend tests
│   │   ├── conftest.py      # Test fixtures
│   │   └── test_*.py        # Test modules
│   ├── pyproject.toml       # Python dependencies
│   ├── alembic.ini          # Alembic configuration
│   ├── dev.env              # Local development config
│   ├── .env.example         # Environment variable documentation
│   ├── Dockerfile           # Backend container image
│   └── docker-entrypoint.sh # Container startup script
├── frontend/
│   ├── src/
│   │   ├── lib/             # Core utilities and services
│   │   │   ├── api-client.ts       # Centralized API client with auth
│   │   │   ├── auth-context.tsx    # Authentication provider
│   │   │   └── utils.ts            # Utility functions
│   │   ├── components/      # Reusable React components
│   │   │   ├── auth/               # Auth-related components
│   │   │   └── layout/             # Layout components
│   │   ├── pages/           # Page components
│   │   ├── types/           # TypeScript type definitions
│   │   ├── App.tsx          # Main app with routing
│   │   └── main.tsx         # Application entry point
│   ├── e2e/                 # Playwright E2E tests
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js   # Material 3 design tokens
│   ├── Dockerfile           # Frontend container image (nginx)
│   └── .nginx-template.conf # Nginx configuration template
├── .github/
│   └── workflows/
│       └── ci.yml           # CI pipeline (lint, test, build)
├── shared_config.json       # Shared configuration (API paths, auth)
├── docker-compose.yml       # Container orchestration
├── start.sh                 # Cross-platform startup script
├── stop.sh                  # Service shutdown script
├── start.bat                # Windows wrapper (calls start.sh via Git Bash)
├── stop.bat                 # Windows shutdown wrapper
└── README.md
```

## Database Schema

The system implements 15 core tables supporting the full investigation workflow:

**Identity & Auth**:
- `users` - Investigator and officer user accounts
- `session_records` - JWT-backed revocable sessions

**Customer & Risk Context**:
- `customers` - Customer profiles
- `risk_profiles` - Risk ratings and compliance flags
- `accounts` - Account relationships
- `transactions` - Transaction history

**Alert & Case Workflow**:
- `alerts` - Prioritized alert queue
- `aml_cases` - Investigation cases
- `case_alert_links` - Alert-to-case continuity
- `case_notes` - Investigation notes with chronology
- `information_requests` - Information request tracking with SLA

**Rule Evaluation**:
- `detection_rule_snapshots` - Immutable historical rule versions
- `rule_evaluation_results` - Rule hit outcomes and explanations

**Governance**:
- `case_decisions` - Four-eyes decision seam (reserved)
- `audit_events` - Append-only audit trail

## Manual Development Setup

If you prefer manual setup over the automated startup script:

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install .

# Install dev dependencies (optional)
pip install pytest httpx mypy ruff

# Copy environment configuration
cp dev.env .env

# Run database migrations
alembic upgrade head

# Seed the database
python app/seed.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Verify build
npm run build

# Run type checking
npm run type-check
```

### 3. Running the Application Manually

**Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

**Frontend:**
```bash
cd frontend
BACKEND_PORT=9000 npm run dev
```

The application will be available at:
- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:9000/api/v1`
- **Health Check**: `http://localhost:9000/health`
- **API Docs**: `http://localhost:9000/docs`

## Running Tests

### Backend Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_alert_integration.py -v
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run type checking
npm run type-check

# Run linting
npm run lint
```

### End-to-End Tests

E2E tests require both backend and frontend to be available with seed data:

```bash
cd frontend
npx playwright install chromium
npx playwright test e2e/smoke_login.spec.ts
```

## Docker Deployment

### Building Images

**Backend:**
```bash
cd backend
docker build -t aml-backend .
```

**Frontend:**
```bash
# Build from repository root (frontend needs root context for shared files)
docker build -t aml-frontend -f frontend/Dockerfile .
```

### Running with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at:
- **Frontend**: `http://localhost`
- **Backend**: `http://localhost:9000`

### PostgreSQL Deployment

For production with PostgreSQL, create `docker-compose.postgres.yml`:

```yaml
version: '3.8'

services:
  database:
    image: postgres:16
    environment:
      POSTGRES_USER: aml_user
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: aml_db
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: backend
      dockerfile: Dockerfile
      args:
        INSTALL_SPEC: ".[postgres]"
    environment:
      DATABASE_URL: postgresql+psycopg://aml_user:secure_password@database:5432/aml_db
    depends_on:
      - database

volumes:
  postgres-data:
```

Run with: `docker-compose -f docker-compose.yml -f docker-compose.postgres.yml up`

## Database Migrations

### Create a new migration

```bash
cd backend
source .venv/bin/activate
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Check migration status

```bash
alembic check
```

### Rollback one migration

```bash
alembic downgrade -1
```

## Environment Variables

### Backend

All backend environment variables are documented in `backend/.env.example`:

- `DATABASE_URL` - Database connection string (default: `sqlite:///./app.db`)
- `JWT_SECRET_KEY` - Secret key for JWT token signing (change in production!)
- `JWT_ALGORITHM` - JWT algorithm (default: `HS256`)
- `JWT_EXPIRATION_MINUTES` - Token expiration time (default: `480`)
- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins
- `DEBUG` - Enable debug mode (default: `true` in dev, `false` in production)
- `RATE_LIMIT_ENABLED` - Enable rate limiting (default: `true`)

### Frontend

- `BACKEND_PORT` - Backend port for Vite dev server proxy (read from environment by start.sh)
- `VITE_API_URL` - Override API base URL (default: `/api` - relative same-origin)

**Note**: Frontend uses same-origin API by default. The dev server proxies `/api` to the backend, and in production nginx handles the routing.

## API Endpoints

All API routes are mounted under `/api/v1`:

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

### Alerts
- `GET /api/v1/alerts` - Get prioritized alert queue with filtering
- `POST /api/v1/alerts/{alert_id}/claim` - Claim/assign alert
- `POST /api/v1/alerts/{alert_id}/triage-disposition` - Save triage decision
- `POST /api/v1/alerts/{alert_id}/cases` - Escalate alert to case

### Cases
- `GET /api/v1/cases/{case_id}` - Get case overview
- `GET /api/v1/cases/{case_id}/notes` - List investigation notes
- `POST /api/v1/cases/{case_id}/notes` - Add investigation note
- `POST /api/v1/cases/{case_id}/status-transitions` - Update case status
- `POST /api/v1/cases/{case_id}/recommendation` - Submit recommendation
- `GET /api/v1/cases/{case_id}/evidence-package` - Get complete evidence
- `GET /api/v1/cases/{case_id}/handoff` - Get review handoff package
- `POST /api/v1/cases/{case_id}/handoff` - Submit for review

### Information Requests
- `POST /api/v1/information-requests` - Create information request
- `GET /api/v1/information-requests?case_id={id}` - List requests for case
- `POST /api/v1/information-requests/{id}/record-response` - Record response

### Audit
- `GET /api/v1/audit-events` - Retrieve audit trail with filters

### Health
- `GET /api/v1/health/ready` - Readiness check with database status

## Design System

The frontend implements Material Design 3 (M3) design system with:

- **Color tokens** extracted from design wireframes
- **Typography scale** based on M3 specifications
- **Spacing system** using 4dp baseline grid
- **Component library** with reusable layout components
- **Accessibility** with 48dp minimum touch targets and semantic HTML

Key design components:
- `AmlTopBar` - Material 3 top app bar with role badge
- `StickyActionFooter` - Fixed bottom action bar for primary CTAs
- `RequireAuth` - Route guard for protected pages

## Security Features

- **Password Security**: bcrypt hashing with cost factor ≥ 12
- **Session Management**: JWT-backed revocable sessions with server-side token storage
- **Token Storage**: SessionStorage for client-side token persistence
- **Input Validation**: Pydantic schemas for all request payloads
- **SQL Injection Protection**: Parameterized queries via ORM exclusively
- **CORS**: Explicit origin allow-list
- **Rate Limiting**: Configurable per-endpoint protection
- **Audit Trail**: Immutable audit events for all security-relevant actions

## CI/CD Pipeline

The GitHub Actions CI workflow (`.github/workflows/ci.yml`) runs on every push and pull request:

### Backend Job
1. Set up Python 3.11
2. Start PostgreSQL service container
3. Install dependencies
4. Run database migrations against PostgreSQL
5. Run ruff linting
6. Run mypy type checking
7. Run pytest test suite

### Frontend Job
1. Set up Node.js 22
2. Install dependencies
3. Run ESLint
4. Run TypeScript type checking
5. Build production bundle

Both jobs must pass for the CI pipeline to succeed.

## Development Workflow

1. **Create feature branch** from `main`
2. **Make changes** to models, schemas, services, routers, or components
3. **Generate migration** if schema changed: `alembic revision --autogenerate -m "..."`
4. **Run backend tests**: `pytest tests/ -v`
5. **Run frontend type check**: `npm run type-check`
6. **Run frontend build**: `npm run build`
7. **Type check backend**: `mypy app --check-untyped-defs`
8. **Verify migration**: `alembic check` and `alembic upgrade head`
9. **Commit changes** with migration file
10. **Open pull request**

## Contributing

When adding new features:

1. Follow the existing layered architecture (models → schemas → repositories → services → routers)
2. Add type hints to all functions and methods
3. Write tests for new functionality (unit, integration, acceptance as appropriate)
4. Generate database migrations for schema changes
5. Follow Material 3 design system for UI components
6. Update this README if adding new endpoints or major features
7. Ensure all CI checks pass before merging

## Troubleshooting

### Port already in use
The startup script automatically finds available ports. If you need specific ports, set them before running:
```bash
export BACKEND_PORT=9000
export FRONTEND_PORT=5173
./start.sh
```

### Database migration errors
If you encounter migration errors, check:
1. Virtual environment is activated
2. All dependencies installed: `pip install .`
3. Migration files are present in `backend/alembic/versions/`
4. Run `alembic current` to see current revision
5. Try `alembic upgrade head` manually to see detailed error

### Frontend build errors
Ensure Node.js version is 20.19+ or 22.12+:
```bash
node --version
```

If npm dependencies fail to install:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Windows-specific issues
- Ensure Git Bash is installed (comes with Git for Windows)
- Run `start.bat` from Command Prompt, not PowerShell
- If Python not found, add Python to PATH during installation

## License

See LICENSE file for details.

## Support

For issues or questions, please open an issue in the project repository.
