import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 01: Alert Queue and Triage', () => {
  test.beforeEach(async ({ page }) => {
    // Login with investigator credentials from seed
    await page.goto('/login');
    
    // Fill login form
    await page.fill('input[name="username"]', 'riya');
    await page.fill('input[name="password"]', 'password123');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for navigation to alerts page
    await page.waitForURL('/alerts', { timeout: 10000 });
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('should load alert queue with filters and pagination', async ({ page }) => {
    // Verify page loaded
    await expect(page.locator('h1', { hasText: 'Alerts' })).toBeVisible();

    // Verify search field present
    const searchField = page.locator('input[type="search"]');
    await expect(searchField).toBeVisible();

    // Verify alert queue loaded
    await page.waitForSelector('[aria-label="Loading alert queue"], article', { timeout: 10000 });

    // Verify pagination info present (wait for data to load)
    await expect(page.locator('text=/Showing \\d+–\\d+ of \\d+/')).toBeVisible({ timeout: 10000 });
  });

  test('should filter alerts by status', async ({ page }) => {
    // Wait for initial load - either loading indicator or alerts
    await page.waitForSelector('[aria-label="Loading alert queue"], article', { timeout: 10000 });

    // Wait for alerts to appear
    await page.waitForSelector('article', { timeout: 10000 });

    // Verify search field is present for filtering
    const searchField = page.locator('input[type="search"]');
    await expect(searchField).toBeVisible();

    // Type in search field to filter
    await searchField.fill('alert-001');

    // Wait for filter to apply
    await page.waitForTimeout(1000);

    // Verify pagination updates
    await expect(page.locator('text=/Showing \\d+–\\d+ of \\d+/')).toBeVisible();
  });

  test('should assign hero alert and enable case creation', async ({ page }) => {
    // Wait for page to load
    await page.waitForSelector('[aria-label="Loading alert queue"], article', { timeout: 10000 });

    // Wait for hero alert card to load
    const heroCard = page.locator('article').first();
    await expect(heroCard).toBeVisible({ timeout: 10000 });

    // Check if "Assign to me" button exists
    const assignButton = heroCard.locator('button', { hasText: 'Assign to me' });
    
    // Assert the button exists
    await expect(assignButton).toBeVisible();
    
    // Click the button
    await assignButton.click();

    // Wait for assignment to complete
    await page.waitForTimeout(2000);

    // After assignment, "Create case" button should be enabled
    const createCaseButton = heroCard.locator('button', { hasText: 'Create case' });
    await expect(createCaseButton).toBeVisible();
    await expect(createCaseButton).toBeEnabled();

    // Verify assignment reflected somewhere on page
    await expect(page.locator('text=/Assigned/')).toBeVisible();
  });

  test('should open triage disposition modal for assigned alert', async ({ page }) => {
    // Wait for queue to load
    await page.waitForSelector('[aria-label="Loading alert queue"], article', { timeout: 10000 });
    await page.waitForSelector('article', { timeout: 10000 });

    // Find the first alert and assign it if not already assigned
    const firstQueueAlert = page.locator('article').nth(1); // Skip hero (0), get first queue item (1)
    
    // Check if needs assignment
    const assignBtn = firstQueueAlert.locator('button', { hasText: 'Assign to me' });
    const triageBtn = firstQueueAlert.locator('button', { hasText: 'Triage' });
    
    // Assign if needed
    if (await assignBtn.isVisible()) {
      await assignBtn.click();
      await page.waitForTimeout(2000);
    }
    
    // Now triage button should be visible
    await expect(triageBtn).toBeVisible();
    await triageBtn.click();

    // Verify modal opened
    await expect(page.locator('[role="dialog"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=/Triage alert/')).toBeVisible();

    // Verify outcome options present
    await expect(page.locator('text=/Escalate to case|Investigate/i')).toBeVisible();
    await expect(page.locator('text=/Close.*false positive|Close.*non.*actionable/i')).toBeVisible();

    // Verify rationale textarea present
    await expect(page.locator('textarea#rationale')).toBeVisible();

    // Close modal
    await page.click('button:has-text("Cancel")');
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test('should validate triage disposition rationale minimum length', async ({ page }) => {
    // Wait for queue to load
    await page.waitForSelector('[aria-label="Loading alert queue"], article', { timeout: 10000 });
    await page.waitForSelector('article', { timeout: 10000 });

    // Get first queue alert and ensure it's assigned
    const firstQueueAlert = page.locator('article').nth(1);
    
    const assignBtn = firstQueueAlert.locator('button', { hasText: 'Assign to me' });
    if (await assignBtn.isVisible()) {
      await assignBtn.click();
      await page.waitForTimeout(2000);
    }

    // Open triage modal
    const triageBtn = firstQueueAlert.locator('button', { hasText: 'Triage' });
    await expect(triageBtn).toBeVisible();
    await triageBtn.click();

    await expect(page.locator('[role="dialog"]')).toBeVisible({ timeout: 5000 });

    // Select an outcome (first radio button)
    const firstOutcome = page.locator('[role="radio"]').first();
    await expect(firstOutcome).toBeVisible();
    await firstOutcome.click();

    // Enter short rationale (less than 10 characters)
    const rationaleField = page.locator('textarea#rationale');
    await expect(rationaleField).toBeVisible();
    await rationaleField.fill('Short');

    // Try to submit
    const submitButton = page.locator('button', { hasText: 'Save disposition' });
    await expect(submitButton).toBeVisible();
    await submitButton.click();

    // Wait a moment for validation
    await page.waitForTimeout(500);

    // Verify error message or that modal is still open (validation prevented submission)
    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible();

    // Enter valid rationale
    await rationaleField.fill('This is a valid rationale with more than 10 characters explaining the decision clearly.');

    // Submit button should still be enabled
    await expect(submitButton).toBeEnabled();
  });
});
