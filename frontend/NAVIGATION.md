# Frontend Navigation Structure

## Overview

The AML Workbench frontend uses a persistent navigation layout with two main sections accessible via top-level tabs.

## Navigation Layout

### AppLayout Component (`src/components/AppLayout.tsx`)

All authenticated pages are wrapped in the `AppLayout` component, which provides:

1. **Header Bar**
   - User information (name and role)
   - Logout button

2. **Primary Navigation Tabs**
   - **Alerts** - Links to `/alerts`
   - **Cases** - Links to `/cases`

The active tab is highlighted with a blue underline indicator.

## Route Structure

### Alerts Section (`/alerts`)

- `/alerts` - Alert queue page (default landing page after login)
- `/alerts/:alertId/evidence` - Alert evidence and rule snapshot details

### Cases Section (`/cases`)

- `/cases` - Cases landing page (lists all cases)
- `/cases/:caseId/investigation` - Case investigation workspace
- `/cases/:caseId/requests/:requestId` - Information request resolution

## Navigation Flow

### From Alerts to Cases

1. User views alert queue at `/alerts`
2. User clicks an alert to view evidence at `/alerts/:alertId/evidence`
3. User clicks "Create case" button
4. User is navigated to `/cases/:caseId/investigation`
5. User can return to cases list via the top "Cases" tab

### Within Cases Section

1. User clicks "Cases" tab to view `/cases`
2. User clicks a case to view `/cases/:caseId/investigation`
3. User clicks an information request to view `/cases/:caseId/requests/:requestId`
4. User can navigate back via the "Back" button or use the top "Cases" tab

### Between Sections

Users can switch between Alerts and Cases sections at any time using the persistent navigation tabs at the top of every page (except login).

## Implementation Details

- Navigation uses React Router's `Link` component for client-side routing
- Active tab detection uses `useLocation` hook to check current pathname
- Navigation is only visible to authenticated users
- Login page does not show navigation (separate route layout)
