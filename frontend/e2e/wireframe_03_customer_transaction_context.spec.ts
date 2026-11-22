import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 03 - Customer and Transaction Context', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    await page.fill('input[name="username"]', 'riya');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/alerts', { timeout: 10000 });
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to evidence page and display customer risk context', async ({ page }) => {
    // Navigate directly to evidence page
    await page.goto('/cases/case-CS-001/evidence');
    await page.waitForLoadState('networkidle');

    // Wait for page to finish loading
    await page.waitForTimeout(1000);

    // Verify customer risk context is displayed
    const customerRiskHeading = page.getByRole('heading', { name: /customer risk context/i });
    await expect(customerRiskHeading).toBeVisible({ timeout: 10000 });

    // Verify risk rating badge is visible
    const riskBadge = page.locator('text=/HIGH risk|MEDIUM risk|LOW risk/').first();
    await expect(riskBadge).toBeVisible();

    // Verify customer name is displayed
    await expect(page.locator('text=/Acme Global Trading|Northstar Trading/').first()).toBeVisible();
  });

  test('should display masked account numbers in account relationships', async ({ page }) => {
    await page.goto('/cases/case-CS-001/evidence');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verify account relationships section
    const accountsHeading = page.getByRole('heading', { name: /account relationships/i });
    await expect(accountsHeading).toBeVisible({ timeout: 10000 });

    // Verify masked account number format (GB•• •••• 4821)
    const maskedAccount = page.locator('text=/GB•• •••• \\d{4}|US•• •••• \\d{4}|CA•• •••• \\d{4}/').first();
    await expect(maskedAccount).toBeVisible();

    // Verify privacy notice
    await expect(page.getByText(/accounts are masked/i)).toBeVisible();
  });

  test('should display transaction timeline with sortable columns', async ({ page }) => {
    await page.goto('/cases/case-CS-001/evidence');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verify transaction timeline section
    const timelineHeading = page.getByRole('heading', { name: /transaction evidence timeline/i });
    await expect(timelineHeading).toBeVisible({ timeout: 10000 });

    // Verify sort chips are present
    const dateChip = page.getByRole('button', { name: /date/i }).first();
    const amountChip = page.getByRole('button', { name: /amount/i }).first();

    await expect(dateChip).toBeVisible();
    await expect(amountChip).toBeVisible();

    // Click amount chip to sort by amount
    await amountChip.click();
    await expect(amountChip).toHaveAttribute('aria-pressed', 'true');

    // Verify transaction details are displayed
    await expect(page.locator('text=/USD|GBP|EUR/').first()).toBeVisible();
  });

  test('should display rule evaluations with historical versions', async ({ page }) => {
    await page.goto('/cases/case-CS-001/evidence');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verify rule-hit rationale section
    const rulesHeading = page.getByRole('heading', { name: /rule-hit rationale/i });
    await expect(rulesHeading).toBeVisible({ timeout: 10000 });

    // Verify immutable banner
    await expect(page.getByText(/historical versions used at evaluation/i)).toBeVisible();

    // Verify rule version is displayed (v3.2, v2.1, v4.0)
    await expect(page.locator('text=/v\\d+\\.\\d+/').first()).toBeVisible();

    // Verify MATCH or PASS outcome badge
    const outcomeBadge = page.locator('text=/MATCH|PASS/').first();
    await expect(outcomeBadge).toBeVisible();
  });

  test('should show top app bar and evidence page structure', async ({ page }) => {
    await page.goto('/cases/case-CS-001/evidence');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verify top app bar is visible
    const appBar = page.locator('header').first();
    await expect(appBar).toBeVisible({ timeout: 10000 });

    // Verify case heading is visible
    const caseHeading = page.getByRole('heading', { name: /evidence/i }).first();
    await expect(caseHeading).toBeVisible();
  });

  test('should allow navigation back to case workspace', async ({ page }) => {
    await page.goto('/cases/case-CS-001/evidence');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Click back button in top app bar
    const backButton = page.locator('button[aria-label*="Navigate up"]').first();
    await expect(backButton).toBeVisible({ timeout: 10000 });
    await backButton.click();
    await page.waitForURL(/\/cases\/case-CS-001$/, { timeout: 10000 });

    // Verify we're back on case workspace
    await expect(page.getByRole('heading', { name: /case summary/i })).toBeVisible({ timeout: 10000 });
  });
});
