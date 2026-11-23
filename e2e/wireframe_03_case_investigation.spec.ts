import { test, expect } from './_pipeline_guard';

test.describe('Screen 3: Case Investigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login with seed credentials
    await page.goto('/login');
    await page.fill('input[type="email"]', 'investigator@example.com');
    await page.fill('input[type="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/alerts');
  });

  test('should display case workspace with tabs', async ({ page }) => {
    // Navigate to case investigation page (using seed case CS-201: 50000000-0000-0000-0000-000000000001)
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/investigation');

    // Verify page loads
    await expect(page.locator('h1')).toContainText('CS-201');
    
    // Verify tabs are present
    await expect(page.getByRole('button', { name: /overview/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /linked alerts/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /requests/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /audit/i })).toBeVisible();
  });

  test('should display linked alerts section', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/investigation');

    // Wait for content to load
    await expect(page.getByText('Linked alerts')).toBeVisible();
    
    // Verify at least one alert card is present
    const alertCards = page.locator('.card');
    await expect(alertCards.first()).toBeVisible();
  });

  test('should switch between tabs', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/investigation');

    // Click on different tabs
    await page.getByRole('button', { name: /linked alerts/i }).click();
    await expect(page.getByRole('button', { name: /linked alerts/i })).toHaveClass(/active/);

    await page.getByRole('button', { name: /overview/i }).click();
    await expect(page.getByRole('button', { name: /overview/i })).toHaveClass(/active/);
  });

  test('should add a note and verify it appears in timeline', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/investigation');

    // Wait for page to load
    await expect(page.getByText('Investigation narrative')).toBeVisible();

    // Select note category (investigation is default)
    await expect(page.locator('.chip-selected')).toContainText('Investigation');

    // Enter note text
    const noteText = 'Test investigation note added during e2e test';
    await page.fill('textarea', noteText);

    // Click save note button
    await page.getByRole('button', { name: /save note/i }).click();

    // Wait for success snackbar
    await expect(page.getByText(/note saved successfully/i)).toBeVisible({ timeout: 5000 });

    // Verify note appears in notes history
    await expect(page.getByText(noteText)).toBeVisible();
  });

  test('should display activity timeline', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/investigation');

    // Verify timeline section is present
    await expect(page.getByText('Activity timeline')).toBeVisible();
    
    // Verify at least one timeline entry exists
    const timelineItems = page.locator('.timeline-item');
    await expect(timelineItems.first()).toBeVisible();
  });
});
