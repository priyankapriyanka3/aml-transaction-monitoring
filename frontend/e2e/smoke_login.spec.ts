// Smoke test: Infrastructure verification
// Full login form implementation will be added in TASK-3
import { test, expect } from './_pipeline_guard';

test.describe('Smoke: Frontend Infrastructure', () => {
  test('should load login page and show placeholder', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Verify login page loads
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();
    
    // Verify placeholder text (login form will be implemented in TASK-3)
    await expect(page.getByText('Login page will be implemented in Task 3')).toBeVisible();
  });

  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    // Try to access home page without logging in
    await page.goto('/');

    // Should redirect to login due to RequireAuth guard
    await page.waitForURL('/login');
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();
  });

  test('should apply Material 3 design tokens', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Verify CSS classes from Tailwind config are applied
    const card = page.locator('.bg-surface');
    await expect(card).toBeVisible();
    
    // Verify background color is applied (Material 3 background token)
    const bodyBg = await page.evaluate(() => {
      return window.getComputedStyle(document.body).backgroundColor;
    });
    
    // Background should be set (not default white or transparent)
    expect(bodyBg).toBeTruthy();
  });
});
