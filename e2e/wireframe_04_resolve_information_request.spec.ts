import { test, expect } from './_pipeline_guard';

test.describe('Screen 4: Resolve Information Request', () => {
  test.beforeEach(async ({ page }) => {
    // Login with seed credentials
    await page.goto('/login');
    await page.fill('input[type="email"]', 'investigator@example.com');
    await page.fill('input[type="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/alerts');
  });

  test('should display information request details', async ({ page }) => {
    // Navigate to request resolution page (using seed request IR-001: a0000000-0000-0000-0000-000000000001 for case CS-201)
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/requests/a0000000-0000-0000-0000-000000000001');

    // Verify page loads with case reference
    await expect(page.locator('h1')).toContainText('CS-');
    
    // Verify request reference is displayed
    await expect(page.getByText(/Request IR-/)).toBeVisible();
    
    // Verify request status badge
    await expect(page.locator('.badge')).toBeVisible();
  });

  test('should display blocker banner for open request', async ({ page }) => {
    // Navigate to open request
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/requests/a0000000-0000-0000-0000-000000000001');

    // Wait for banner to appear
    const banner = page.locator('[role="status"]').first();
    await expect(banner).toBeVisible();
    
    // Verify blocker message is present
    await expect(banner).toContainText(/decision blocked/i);
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/requests/a0000000-0000-0000-0000-000000000001');

    // Try to submit without filling fields
    const recordButton = page.getByRole('button', { name: /record response/i });
    
    // Button should be disabled when fields are empty
    await expect(recordButton).toBeDisabled();
  });

  test('should fill response form and enable submit button', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/requests/a0000000-0000-0000-0000-000000000001');

    // Fill response summary
    const responseSummary = 'Customer provided comprehensive documentation including bank statements and invoices.';
    await page.fill('textarea', responseSummary);

    // Fill received date (today or past date)
    const today = new Date().toISOString().split('T')[0];
    await page.fill('input[type="date"]', today);

    // Button should be enabled now
    const recordButton = page.getByRole('button', { name: /record response/i });
    await expect(recordButton).not.toBeDisabled();
  });

  test('should record response and show success message', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/requests/a0000000-0000-0000-0000-000000000001');

    // Fill response form
    const responseSummary = 'Test response: Customer provided all required documentation.';
    await page.fill('textarea', responseSummary);

    const today = new Date().toISOString().split('T')[0];
    await page.fill('input[type="date"]', today);

    // Click record response button
    await page.getByRole('button', { name: /record response/i }).click();

    // Wait for success snackbar
    await expect(page.getByText(/response recorded/i)).toBeVisible({ timeout: 5000 });
  });

  test('should show discard dialog when navigating back with unsaved changes', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/requests/a0000000-0000-0000-0000-000000000001');

    // Enter some text in response summary
    await page.fill('textarea', 'Some unsaved text');

    // Click back button
    await page.getByLabel(/back to case investigation/i).click();

    // Verify discard dialog appears
    await expect(page.getByRole('alertdialog')).toBeVisible();
    await expect(page.getByText(/discard unsaved response/i)).toBeVisible();
  });

  test('should not show discard dialog when navigating back without changes', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/requests/a0000000-0000-0000-0000-000000000001');

    // Don't enter any text, just click back
    await page.getByLabel(/back to case investigation/i).click();

    // Should navigate directly without dialog
    await page.waitForURL(/\/cases\/.+\/investigation/, { timeout: 2000 });
  });

  test('should display request details fields', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/requests/a0000000-0000-0000-0000-000000000001');

    // Verify detail list contains expected fields
    await expect(page.getByText('Due date')).toBeVisible();
    await expect(page.getByText('Target')).toBeVisible();
    await expect(page.getByText('Channel')).toBeVisible();
    await expect(page.getByText('Reason')).toBeVisible();
    await expect(page.getByText('Raised')).toBeVisible();
  });
});
