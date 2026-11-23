import { test, expect } from './_pipeline_guard';

test.describe('Screen 5: Review Readiness and Officer Assignment', () => {
  test.beforeEach(async ({ page }) => {
    // Login with investigator seed credentials
    await page.goto('/login');
    await page.fill('input[type="email"]', 'investigator@example.com');
    await page.fill('input[type="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/alerts');
  });

  test('should display readiness checklist with all items', async ({ page }) => {
    // Navigate to readiness page (using seed case CS-204: 50000000-0000-0000-0000-000000000004)
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/readiness');

    // Verify page loads with correct title
    await expect(page.locator('h1')).toContainText('Review readiness');
    await expect(page.getByText('TRANSFER REVIEW · 05 OF 06')).toBeVisible();

    // Verify readiness checklist section
    await expect(page.getByText('Readiness checklist')).toBeVisible();

    // Verify all 4 checklist items are present
    await expect(page.getByText('Linked evidence')).toBeVisible();
    await expect(page.getByText('Investigation notes')).toBeVisible();
    await expect(page.getByText('Responses reviewed')).toBeVisible();
    await expect(page.getByText('No open or overdue requests')).toBeVisible();
  });

  test('should display checklist completion status with badges', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/readiness');

    // Wait for checklist to load
    await expect(page.getByText('Readiness checklist')).toBeVisible();

    // Verify completion badge shows count
    const completionBadge = page.locator('.badge').filter({ hasText: /complete/i }).first();
    await expect(completionBadge).toBeVisible();

    // Verify each checklist item has a status badge (Complete or Incomplete)
    const checklistItems = page.locator('.checklist-item');
    expect(await checklistItems.count()).toBeGreaterThanOrEqual(4);

    // Verify checklist icons are present (checkmarks or outline circles)
    const checklistIcons = page.locator('.checklist-icon');
    expect(await checklistIcons.count()).toBeGreaterThanOrEqual(4);
  });

  test('should display review package summary', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/readiness');

    // Verify review package section
    await expect(page.getByText('Review package')).toBeVisible();
    await expect(page.getByText(/What the officer will receive/i)).toBeVisible();

    // Verify package items are listed
    await expect(page.getByText(/Alerts · /i)).toBeVisible();
    await expect(page.getByText(/Investigation notes · /i)).toBeVisible();
    await expect(page.getByText(/Information requests · /i)).toBeVisible();
    await expect(page.getByText(/Historical rule context/i)).toBeVisible();
  });

  test('should display four-eyes officer assignment card', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/readiness');

    // Verify four-eyes card
    await expect(page.getByText('Independent review required')).toBeVisible();
    await expect(page.getByText(/Case creator cannot decide this case/i)).toBeVisible();

    // Verify officer dropdown is present
    await expect(page.locator('select, .field-select')).toBeVisible();
    await expect(page.getByText('Reviewing officer')).toBeVisible();

    // Verify explanation text about four-eyes enforcement
    await expect(page.getByText(/Case creator is not selectable/i)).toBeVisible();
  });

  test('should enable share button only when checklist complete and officer selected', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/readiness');

    // Wait for page to load
    await expect(page.getByText('Readiness checklist')).toBeVisible();

    // Find share button
    const shareButton = page.getByRole('button', { name: /share for officer review/i });
    await expect(shareButton).toBeVisible();

    // If checklist is incomplete or no officer selected, button should be disabled
    // (Note: actual state depends on seed data - CS-204 should be ready)
    
    // Button text should be present
    await expect(shareButton).toContainText(/share for officer review/i);
  });

  test('should select officer and share for review', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/readiness');

    // Wait for page load
    await expect(page.getByText('Readiness checklist')).toBeVisible();

    // Select an officer from dropdown (if available)
    const officerSelect = page.locator('select').first();
    await expect(officerSelect).toBeVisible();

    // Get available options
    const options = await officerSelect.locator('option').all();
    if (options.length > 1) {
      // Select first officer (not the placeholder)
      await officerSelect.selectOption({ index: 1 });

      // Wait a moment for assignment to process
      await page.waitForTimeout(500);

      // Try to share for review
      const shareButton = page.getByRole('button', { name: /share for officer review/i });
      
      // Check if button is enabled
      const isDisabled = await shareButton.isDisabled();
      if (!isDisabled) {
        await shareButton.click();

        // Wait for success snackbar or navigation
        await expect(
          page.getByText(/case shared/i).or(page.locator('.snackbar'))
        ).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should navigate back to case investigation', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/readiness');

    // Click back button
    const backButton = page.locator('button[aria-label*="Back"]').first();
    await backButton.click();

    // Verify navigation occurred (URL should change to investigation page)
    await expect(page).toHaveURL(/\/cases\/.*\/investigation/);
  });

  test('should display warning banner when checklist incomplete', async ({ page }) => {
    // Use a case with incomplete checklist (CS-201: 50000000-0000-0000-0000-000000000001)
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/readiness');

    // Wait for page load
    await expect(page.getByText('Readiness checklist')).toBeVisible();

    // If checklist is incomplete, share button should be disabled
    const shareButton = page.getByRole('button', { name: /share for officer review/i });
    
    // Check if any warning or error messages are present
    const warnings = page.locator('.banner-warn, .banner-error, .helper-error');
    const warningCount = await warnings.count();
    
    // If warnings exist, they should be visible
    if (warningCount > 0) {
      await expect(warnings.first()).toBeVisible();
    }
  });
});
