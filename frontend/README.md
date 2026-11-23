# AML Transaction Monitoring Workbench - Frontend

React + TypeScript frontend for the AML Transaction Monitoring system, implementing wireframes 01-04 (Alert Queue, Evidence, Case Investigation, and Request Resolution screens).

## Stack

- **React 18** - UI library
- **TypeScript 5** - Type safety
- **Vite 5** - Build tool and dev server
- **Zustand** - State management
- **React Router** - Client-side routing
- **Playwright** - End-to-end testing

## Design System

Implements Material Design 3 semantics from `design.md`:
- Color scheme: Primary #005FCC, compliance status colors (Critical, Warning, Success, Info)
- Typography: Inter font family with M3 scale
- Spacing: 4dp baseline grid
- Components: Cards, badges, buttons, chips, banners, search fields

## Project Structure

```
src/
├── api/          # API client and backend communication
├── components/   # Shared layout components (AppLayout with navigation)
├── pages/        # Screen components (Login, AlertQueue, AlertEvidence, Cases, CaseInvestigation, RequestResolution)
├── stores/       # Zustand state management
├── styles/       # Design system CSS
└── types/        # TypeScript type definitions
```

## Navigation

The app features a persistent navigation bar with two main sections:
- **Alerts** - Alert queue and evidence screens
- **Cases** - Cases list, investigation, and request resolution screens

Users can navigate between these sections via the top navigation tabs visible on all authenticated pages.

## Development

### Prerequisites

- Node.js 20.19.0+ or 22.12.0+
- Backend running on port 9000

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Frontend will be available at http://localhost:5173

The dev server proxies `/api` requests to the backend at http://localhost:9000.

### Build for Production

```bash
npm run build
```

Output in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Type Checking

```bash
npm run typecheck
```

### Linting

```bash
npm run lint
```

## Authentication

Default seed credentials:
- **Investigator:** investigator@example.com / investigator123
- **Officer:** officer@example.com / officer123

The login page pre-fills investigator credentials.

## API Integration

API client (`src/api/client.ts`) communicates with backend via relative `/api` paths:
- POST `/api/v1/auth/login` - User authentication
- GET `/api/v1/alerts` - Alert queue with filters
- POST `/api/v1/alerts/{id}/assign` - Assign alert to current user
- GET `/api/v1/alerts/{id}/evidence` - Alert evidence with rule snapshots
- POST `/api/v1/cases` - Create case from alert
- GET `/api/v1/cases/{caseId}/workspace` - Case workspace with notes, alerts, timeline
- POST `/api/v1/cases/{caseId}/notes` - Add investigation note
- GET `/api/v1/cases/{caseId}/requests/{requestId}` - Information request details
- POST `/api/v1/cases/{caseId}/requests/{requestId}/response` - Record request response

Bearer tokens stored in localStorage, sent in Authorization header.

## Testing

### Unit Tests

(To be implemented with Vitest)

### End-to-End Tests

```bash
cd /repos/aml-transaction-monitoring
npx playwright test
```

Test specs:
- `e2e/wireframe_01_alert_queue.spec.ts` - Alert queue screen behaviors
- `e2e/wireframe_02_alert_evidence.spec.ts` - Evidence screen behaviors
- `e2e/wireframe_03_case_investigation.spec.ts` - Case investigation workspace behaviors
- `e2e/wireframe_04_resolve_information_request.spec.ts` - Request resolution behaviors

Tests require:
1. Backend running with seed data loaded
2. Frontend build available for preview server

## Implemented Screens

### Screen 1: Alert Queue (wireframe_01)
**Route:** `/alerts`

Features:
- Highest-priority-first ordering
- Search by alert ID or customer name
- Filter by priority, ownership, status
- Hero alert card for highest priority
- Assign to me action with audit trail
- Navigation to evidence screen

### Screen 2: Alert Evidence (wireframe_02)
**Route:** `/alerts/:alertId/evidence`

Features:
- Transaction facts with amount, customer, account, corridor
- Historical rule evaluation snapshots (read-only)
- Rule name + version display (e.g., "v3.2")
- MATCH/PASS outcome badges
- Create case action
- Navigate back to queue
- Navigation to case investigation after case creation

### Screen 3: Case Investigation (wireframe_03)
**Route:** `/cases/:caseId/investigation`

Features:
- Case workspace with secondary tabs (Overview, Linked alerts, Requests, Audit)
- Linked alerts section with primary/linked badges
- Investigation narrative editor with category selection
- Note autosave with author and timestamp capture
- Notes history display (append-only)
- Activity timeline from audit events
- Decision blocker banner when requests are open/overdue
- Evidence gap identification (future)

### Screen 4: Request Resolution (wireframe_04)
**Route:** `/cases/:caseId/requests/:requestId`

Features:
- Information request details (due date, target, channel, reason)
- Decision blocker warning banner for open/overdue requests
- Response capture form (summary, received date)
- Form validation (required fields)
- Date picker with future date prevention
- Unsaved draft guard (discard dialog on back navigation)
- Response recording with blocker clearance
- Navigation back to case workspace after recording

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Configuration

### Environment Variables

Create `.env` (optional):

```
VITE_API_URL=/api
```

Default: `/api` (relative to frontend origin)

### Proxy Configuration

`vite.config.ts` proxies `/api` to backend. Adjust `BACKEND_PORT` environment variable if backend runs on different port:

```bash
BACKEND_PORT=8000 npm run dev
```

## Deployment

1. Build frontend: `npm run build`
2. Serve `dist/` directory with any static file server
3. Configure server to:
   - Serve `index.html` for all routes (SPA fallback)
   - Proxy `/api` to backend
4. Set `BACKEND_HOST` build arg in Docker to point frontend nginx to backend service

## Stack Deviation Note

Original design specified Android/Kotlin + Jetpack Compose. Implemented as React/TypeScript web app because:
- Pipeline supports only Python + Node.js/TypeScript stacks
- Backend API contracts preserved
- Material 3 design semantics maintained in web form
- Same user workflows and compliance controls

See `/repos/aml-transaction-monitoring/STACK_DEVIATION.md` for details.
