import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 01 - Alert Queue', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Login with seed credentials
    await page.fill('input[type="email"]', 'investigator@example.com');
    await page.fill('input[type="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    
    // Wait for navigation to alerts page
    await page.waitForURL('/alerts');
  });

  test('displays hero alert with priority, score, and transaction details', async ({ page }) => {
    // Wait for alerts to load
    await expect(page.locator('h1')).toContainText('Alerts');
    
    // Verify hero alert card exists and has expected content
    const heroCard = page.locator('article.card-hero').first();
    await expect(heroCard).toBeVisible();
    
    // Check alert reference is displayed
    await expect(heroCard.locator('h3')).toBeVisible();
    
    // Check priority badge with score is visible
    const priorityBadge = heroCard.locator('.badge').first();
    await expect(priorityBadge).toBeVisible();
    await expect(priorityBadge).toContainText(/Critical|High|Medium|Low/);
    await expect(priorityBadge).toContainText(/Score \d+/);
    
    // Check transaction amount is displayed
    await expect(heroCard.locator('.title-large')).toBeVisible();
    
    // Check corridor badge (country codes)
    const corridorBadge = heroCard.locator('.badge-neutral');
    await expect(corridorBadge).toBeVisible();
    await expect(corridorBadge).toContainText(/→/);
    
    // Check customer name is displayed
    await expect(heroCard).toContainText(/Customer:/);
  });

  test('filters alerts by priority using filter chips', async ({ page }) => {
    // Wait for alerts to load
    await expect(page.locator('h1')).toContainText('Alerts');
    
    // Get initial alert count
    const countText = await page.locator('.title-small').first().textContent();
    const initialCount = parseInt(countText?.match(/(\d+) alerts/)?.[1] || '0');
    
    // Click Priority: All chip (if not already selected)
    const priorityChip = page.locator('button.chip').filter({ hasText: 'Priority: All' });
    await priorityChip.click();
    
    // Verify filter is applied (chip should be selected)
    await expect(priorityChip).toHaveClass(/chip-selected/);
    
    // Alert count should be visible
    expect(initialCount).toBeGreaterThan(0);
  });

  test('assigns an alert and displays success snackbar', async ({ page }) => {
    // Wait for alerts to load
    await expect(page.locator('h1')).toContainText('Alerts');
    
    // Find an unassigned alert with "Assign to me" button
    const assignButton = page.locator('button').filter({ hasText: 'Assign to me' }).first();
    
    if (await assignButton.count() === 0) {
      // No unassigned alerts - adjust filters
      const unassignedChip = page.locator('button.chip').filter({ hasText: 'Owner: Unassigned' });
      if (await unassignedChip.count() > 0) {
        await unassignedChip.click();
      }
      const newStatusChip = page.locator('button.chip').filter({ hasText: 'Status: New' });
      if (await newStatusChip.count() > 0) {
        await newStatusChip.click();
      }
      
      // Wait a bit for filters to apply
      await page.waitForTimeout(1000);
    }
    
    // Get alert ref before assigning
    const alertCard = assignButton.locator('..').locator('..');
    const alertRefElement = alertCard.locator('h3').first();
    const alertRef = await alertRefElement.textContent();
    
    // Click assign button
    await assignButton.click();
    
    // Wait for snackbar to appear
    const snackbar = page.locator('.snackbar');
    await expect(snackbar).toBeVisible({ timeout: 5000 });
    
    // Verify snackbar message contains alert reference
    if (alertRef) {
      await expect(snackbar).toContainText(alertRef);
    }
    await expect(snackbar).toContainText('assigned to you');
  });

  test('displays audit guidance banner', async ({ page }) => {
    // Wait for alerts to load
    await expect(page.locator('h1')).toContainText('Alerts');
    
    // Find and verify audit banner
    const auditBanner = page.locator('aside.banner-info');
    await expect(auditBanner).toBeVisible();
    await expect(auditBanner).toContainText('Every action here is audited');
    await expect(auditBanner).toContainText('audit trail');
  });

  test('navigates to alert evidence when clicking alert card', async ({ page }) => {
    // Wait for alerts to load
    await expect(page.locator('h1')).toContainText('Alerts');
    
    // Click on the first alert card (hero or regular)
    const firstCard = page.locator('article.card').first();
    await firstCard.click();
    
    // Wait for navigation to evidence page
    await page.waitForURL(/\/alerts\/.*\/evidence/);
    
    // Verify we're on evidence page
    await expect(page.locator('button').filter({ hasText: 'Back' })).toBeVisible();
  });
});
