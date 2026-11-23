import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 02 - Alert Evidence', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Login with seed credentials
    await page.fill('input[type="email"]', 'investigator@example.com');
    await page.fill('input[type="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    
    // Wait for navigation to alerts page
    await page.waitForURL('/alerts');
    
    // Click on the first alert to view evidence
    const firstCard = page.locator('article.card').first();
    await firstCard.click();
    
    // Wait for evidence page to load
    await page.waitForURL(/\/alerts\/.*\/evidence/);
  });

  test('displays transaction facts with amount, customer, and corridor', async ({ page }) => {
    // Verify evidence page is loaded
    await expect(page.locator('h2#facts-h')).toContainText('Transaction facts');
    
    // Check transaction amount is displayed prominently
    const amountElement = page.locator('.title-large.text-bold').first();
    await expect(amountElement).toBeVisible();
    await expect(amountElement).toContainText(/USD|EUR|GBP|CNY/);
    
    // Verify customer name is present
    await expect(page.locator('text=Customer')).toBeVisible();
    
    // Verify transaction reference is present
    await expect(page.locator('text=Transaction')).toBeVisible();
    
    // Verify date and time
    await expect(page.locator('text=Date and time')).toBeVisible();
    
    // Verify account details
    await expect(page.locator('text=Account')).toBeVisible();
    
    // Verify corridor information
    await expect(page.locator('text=Corridor')).toBeVisible();
  });

  test('displays rule evaluation snapshots with version strings and outcome badges', async ({ page }) => {
    // Verify rule evaluation section header
    await expect(page.locator('h2#rules-h')).toContainText('Rule evaluation snapshot');
    
    // Verify read-only badge
    const readOnlyBadge = page.locator('.badge-neutral').filter({ hasText: 'Read-only' });
    await expect(readOnlyBadge).toBeVisible();
    
    // Verify historical version notice
    const notice = page.locator('.banner-info').filter({ hasText: 'Historical versions' });
    await expect(notice).toBeVisible();
    await expect(notice).toContainText('not the latest rules');
    
    // Check that at least one rule row exists
    const ruleRows = page.locator('.rule-row');
    await expect(ruleRows.first()).toBeVisible();
    
    // Verify rule name with version is displayed
    const firstRuleName = ruleRows.first().locator('.body-medium.text-semibold');
    await expect(firstRuleName).toBeVisible();
    const ruleText = await firstRuleName.textContent();
    expect(ruleText).toMatch(/v\d+\.\d+/); // Version pattern like v2.1, v3.2
    
    // Verify outcome badge (MATCH or PASS)
    const outcomeBadge = ruleRows.first().locator('.badge');
    await expect(outcomeBadge).toBeVisible();
    await expect(outcomeBadge).toContainText(/MATCH|PASS/);
    
    // Check condition text is displayed
    const conditionText = ruleRows.first().locator('.body-small.text-muted').first();
    await expect(conditionText).toBeVisible();
  });

  test('displays MATCH and PASS outcomes distinctly', async ({ page }) => {
    // Get all rule rows
    const ruleRows = page.locator('.rule-row');
    const count = await ruleRows.count();
    
    if (count > 0) {
      // Check that at least one badge exists
      const badges = ruleRows.locator('.badge');
      await expect(badges.first()).toBeVisible();
      
      // Verify badges contain either MATCH or PASS
      for (let i = 0; i < Math.min(count, 3); i++) {
        const badge = badges.nth(i);
        await expect(badge).toContainText(/MATCH|PASS/);
      }
    }
  });

  test('displays summary of matched and passed rules', async ({ page }) => {
    // Verify summary text at bottom of rules section
    const summary = page.locator('.body-small.text-muted').filter({ 
      hasText: /rules matched.*rules passed/
    });
    await expect(summary).toBeVisible();
    await expect(summary).toContainText('Snapshots are stored at evaluation time and cannot be edited');
  });

  test('creates case and displays success snackbar', async ({ page }) => {
    // Get alert reference from page title
    const alertRef = await page.locator('h1.title-large').textContent();
    
    // Click "Create case" button
    const createButton = page.locator('button.btn-filled').filter({ hasText: 'Create case' });
    await createButton.click();
    
    // Wait for snackbar to appear
    const snackbar = page.locator('.snackbar');
    await expect(snackbar).toBeVisible({ timeout: 10000 });
    
    // Verify snackbar shows case created message
    await expect(snackbar).toContainText(/Case CS-\d+ created/);
    
    // Verify snackbar has action button
    const actionButton = snackbar.locator('button.snackbar-action');
    await expect(actionButton).toBeVisible();
    await expect(actionButton).toContainText('View case');
  });

  test('navigates back to alert queue', async ({ page }) => {
    // Click back button
    const backButton = page.locator('button').filter({ hasText: 'Back' });
    await backButton.click();
    
    // Verify we're back on alerts page
    await page.waitForURL('/alerts');
    await expect(page.locator('h1.headline-large')).toContainText('Alerts');
  });

  test('displays alert status and priority badges', async ({ page }) => {
    // Verify status badge
    const statusBadge = page.locator('.badge-info').filter({ hasText: /Status:/ });
    await expect(statusBadge).toBeVisible();
    
    // Verify priority badge with score
    const priorityBadge = page.locator('.badge').filter({ hasText: /Critical|High|Medium|Low/ }).first();
    await expect(priorityBadge).toBeVisible();
    await expect(priorityBadge).toContainText(/Score \d+/);
    
    // Verify corridor badge
    const corridorBadge = page.locator('.badge-neutral').filter({ hasText: /→/ });
    await expect(corridorBadge).toBeVisible();
  });

  test('displays record relationship chain', async ({ page }) => {
    // Find the relationship chain section
    const chain = page.locator('[aria-label="Record relationship"]');
    await expect(chain).toBeVisible();
    
    // Verify it contains alert ref, transaction ref, and customer name
    // The chain should have arrow symbols between nodes
    await expect(chain).toContainText('→');
  });
});
