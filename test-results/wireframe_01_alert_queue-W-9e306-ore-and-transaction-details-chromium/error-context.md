# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: wireframe_01_alert_queue.spec.ts >> Wireframe 01 - Alert Queue >> displays hero alert with priority, score, and transaction details
- Location: e2e/wireframe_01_alert_queue.spec.ts:17:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('article.card-hero').first()
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" locator('article.card-hero').first() with timeout 5000ms
  - waiting for locator('article.card-hero').first()

```

```yaml
- banner:
  - paragraph: TRANSFER REVIEW · Alice Investigator · INVESTIGATOR
  - text: INVESTIGATOR
  - button "Logout"
  - navigation "Main navigation":
    - link "Alerts":
      - /url: /alerts
    - link "Cases":
      - /url: /cases
- main:
  - heading "Alerts" [level=1]
  - paragraph: Review queue / highest priority first
  - text: 🔍
  - searchbox "Search alerts"
  - group "Queue filters":
    - 'button "✓ ✓ Priority: All"'
    - 'button "✓ ✓ Owner: Unassigned"'
    - 'button "✓ ✓ Status: New"'
  - heading "0 alerts · highest priority first" [level=2]
  - text: Refreshed 22/11/2026, 12:52:51 UTC
  - paragraph: No alerts match these filters
  - paragraph: Clear a filter to see more alerts.
```

# Test source

```ts
  1   | import { test, expect } from '@playwright/test';
  2   | 
  3   | test.describe('Wireframe 01 - Alert Queue', () => {
  4   |   test.beforeEach(async ({ page }) => {
  5   |     // Navigate to login page
  6   |     await page.goto('/login');
  7   |     
  8   |     // Login with seed credentials
  9   |     await page.fill('input[type="email"]', 'investigator@example.com');
  10  |     await page.fill('input[type="password"]', 'investigator123');
  11  |     await page.click('button[type="submit"]');
  12  |     
  13  |     // Wait for navigation to alerts page
  14  |     await page.waitForURL('/alerts');
  15  |   });
  16  | 
  17  |   test('displays hero alert with priority, score, and transaction details', async ({ page }) => {
  18  |     // Wait for alerts to load
  19  |     await expect(page.locator('h1')).toContainText('Alerts');
  20  |     
  21  |     // Verify hero alert card exists and has expected content
  22  |     const heroCard = page.locator('article.card-hero').first();
> 23  |     await expect(heroCard).toBeVisible();
      |                            ^ Error: expect(locator).toBeVisible() failed
  24  |     
  25  |     // Check alert reference is displayed
  26  |     await expect(heroCard.locator('h3')).toBeVisible();
  27  |     
  28  |     // Check priority badge with score is visible
  29  |     const priorityBadge = heroCard.locator('.badge').first();
  30  |     await expect(priorityBadge).toBeVisible();
  31  |     await expect(priorityBadge).toContainText(/Critical|High|Medium|Low/);
  32  |     await expect(priorityBadge).toContainText(/Score \d+/);
  33  |     
  34  |     // Check transaction amount is displayed
  35  |     await expect(heroCard.locator('.title-large')).toBeVisible();
  36  |     
  37  |     // Check corridor badge (country codes)
  38  |     const corridorBadge = heroCard.locator('.badge-neutral');
  39  |     await expect(corridorBadge).toBeVisible();
  40  |     await expect(corridorBadge).toContainText(/→/);
  41  |     
  42  |     // Check customer name is displayed
  43  |     await expect(heroCard).toContainText(/Customer:/);
  44  |   });
  45  | 
  46  |   test('filters alerts by priority using filter chips', async ({ page }) => {
  47  |     // Wait for alerts to load
  48  |     await expect(page.locator('h1')).toContainText('Alerts');
  49  |     
  50  |     // Get initial alert count
  51  |     const countText = await page.locator('.title-small').first().textContent();
  52  |     const initialCount = parseInt(countText?.match(/(\d+) alerts/)?.[1] || '0');
  53  |     
  54  |     // Click Priority: All chip (if not already selected)
  55  |     const priorityChip = page.locator('button.chip').filter({ hasText: 'Priority: All' });
  56  |     await priorityChip.click();
  57  |     
  58  |     // Verify filter is applied (chip should be selected)
  59  |     await expect(priorityChip).toHaveClass(/chip-selected/);
  60  |     
  61  |     // Alert count should be visible
  62  |     expect(initialCount).toBeGreaterThan(0);
  63  |   });
  64  | 
  65  |   test('assigns an alert and displays success snackbar', async ({ page }) => {
  66  |     // Wait for alerts to load
  67  |     await expect(page.locator('h1')).toContainText('Alerts');
  68  |     
  69  |     // Find an unassigned alert with "Assign to me" button
  70  |     const assignButton = page.locator('button').filter({ hasText: 'Assign to me' }).first();
  71  |     
  72  |     if (await assignButton.count() === 0) {
  73  |       // No unassigned alerts - adjust filters
  74  |       const unassignedChip = page.locator('button.chip').filter({ hasText: 'Owner: Unassigned' });
  75  |       if (await unassignedChip.count() > 0) {
  76  |         await unassignedChip.click();
  77  |       }
  78  |       const newStatusChip = page.locator('button.chip').filter({ hasText: 'Status: New' });
  79  |       if (await newStatusChip.count() > 0) {
  80  |         await newStatusChip.click();
  81  |       }
  82  |       
  83  |       // Wait a bit for filters to apply
  84  |       await page.waitForTimeout(1000);
  85  |     }
  86  |     
  87  |     // Get alert ref before assigning
  88  |     const alertCard = assignButton.locator('..').locator('..');
  89  |     const alertRefElement = alertCard.locator('h3').first();
  90  |     const alertRef = await alertRefElement.textContent();
  91  |     
  92  |     // Click assign button
  93  |     await assignButton.click();
  94  |     
  95  |     // Wait for snackbar to appear
  96  |     const snackbar = page.locator('.snackbar');
  97  |     await expect(snackbar).toBeVisible({ timeout: 5000 });
  98  |     
  99  |     // Verify snackbar message contains alert reference
  100 |     if (alertRef) {
  101 |       await expect(snackbar).toContainText(alertRef);
  102 |     }
  103 |     await expect(snackbar).toContainText('assigned to you');
  104 |   });
  105 | 
  106 |   test('displays audit guidance banner', async ({ page }) => {
  107 |     // Wait for alerts to load
  108 |     await expect(page.locator('h1')).toContainText('Alerts');
  109 |     
  110 |     // Find and verify audit banner
  111 |     const auditBanner = page.locator('aside.banner-info');
  112 |     await expect(auditBanner).toBeVisible();
  113 |     await expect(auditBanner).toContainText('Every action here is audited');
  114 |     await expect(auditBanner).toContainText('audit trail');
  115 |   });
  116 | 
  117 |   test('navigates to alert evidence when clicking alert card', async ({ page }) => {
  118 |     // Wait for alerts to load
  119 |     await expect(page.locator('h1')).toContainText('Alerts');
  120 |     
  121 |     // Click on the first alert card (hero or regular)
  122 |     const firstCard = page.locator('article.card').first();
  123 |     await firstCard.click();
```