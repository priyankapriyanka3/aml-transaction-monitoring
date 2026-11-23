# Navigation Diagram

## Visual Navigation Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  AppLayout (Header + Navigation)                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ TRANSFER REVIEW · User Name · Role            [Role] Logout  ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  [Alerts]     [Cases]                                        ││
│  │   ═════                                                       ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
    ┌─────▼──────┐                         ┌─────▼──────┐
    │   ALERTS   │                         │   CASES    │
    │  Section   │                         │  Section   │
    └─────┬──────┘                         └─────┬──────┘
          │                                      │
    ┌─────▼──────────────────────┐        ┌─────▼──────────────────────┐
    │                            │        │                            │
    │  /alerts                   │        │  /cases                    │
    │  Alert Queue Page          │        │  Cases Landing Page        │
    │  - Search & filters        │        │  - List of all cases       │
    │  - Hero alert card         │        │  - Case status badges      │
    │  - Secondary alert cards   │        │  - Click to investigate    │
    │  - Assign to me action     │        │                            │
    │                            │        │                            │
    └─────┬──────────────────────┘        └─────┬──────────────────────┘
          │                                      │
    Click │ alert card                   Click  │ case card
          │                                      │
    ┌─────▼──────────────────────┐        ┌─────▼──────────────────────┐
    │                            │        │                            │
    │  /alerts/:alertId/evidence │        │  /cases/:caseId/           │
    │  Alert Evidence Page       │        │     investigation          │
    │  - Transaction facts       │        │  Case Investigation Page   │
    │  - Customer context        │        │  - Tabs: Overview, Linked  │
    │  - Rule snapshots          │        │    alerts, Requests, Audit │
    │  - MATCH/PASS badges       │        │  - Narrative editor        │
    │  - Create case button      │        │  - Evidence gaps           │
    │  - Back to queue          │        │  - Activity timeline        │
    │                            │        │  - Request info action     │
    └─────┬──────────────────────┘        └─────┬──────────────────────┘
          │                                      │
   Create │ case                         Click   │ request card
   case   │                                      │
          │                            ┌─────────▼──────────────────────┐
          └────────────────────────────▶                                │
                                       │  /cases/:caseId/requests/      │
                                       │     :requestId                 │
                                       │  Request Resolution Page       │
                                       │  - Decision blocker banner     │
                                       │  - Request details             │
                                       │  - Response form               │
                                       │  - Request history timeline    │
                                       │  - Record response action      │
                                       │  - Back to investigation       │
                                       │                                │
                                       └────────────────────────────────┘
```

## Key Navigation Elements

### Top-Level Tabs (Always Visible When Authenticated)
- **Alerts** - Primary blue underline when active
- **Cases** - Primary blue underline when active

### Page-Level Navigation
- **Back buttons** - Return to parent view (e.g., Evidence → Queue)
- **Card clicks** - Navigate to detail views
- **Action buttons** - Create case, Record response, etc.

### Navigation States
- **Active tab** - Blue text, bold font, blue underline
- **Inactive tab** - Gray text, regular font, no underline
- **Clickable cards** - Cursor pointer, full card area clickable

## User Journey Examples

### Create and Investigate a Case
1. Start at `/alerts` (Alert Queue)
2. Click alert → `/alerts/:alertId/evidence`
3. Click "Create case" → `/cases/:caseId/investigation`
4. View case details with tabs
5. Click "Cases" tab → `/cases` to see all cases

### Resolve an Information Request
1. Start at `/cases/:caseId/investigation`
2. Click request card → `/cases/:caseId/requests/:requestId`
3. Fill response form
4. Click "Record response" → Back to `/cases/:caseId/investigation`
5. Case blocker cleared, continue investigation
