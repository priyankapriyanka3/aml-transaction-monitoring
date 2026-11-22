// E2E test for wireframe_05 - Review Handoff
import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 05 - Review Handoff', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // Fill in credentials
    await page.fill('input[name="username"]', 'riya');
    await page.fill('input[name="password"]', 'password123');
    
    // Click login button
    await page.click('button[type="submit"]');
    
    // Wait for navigation to alerts page
    await page.waitForURL('/alerts', { timeout: 15000 });
  });

  test('should navigate to review handoff page', async ({ page }) => {
    // Navigate to handoff page for case-CS-002 (which should be ready based on seed)
    await page.goto('/cases/case-CS-002/handoff');
    await page.waitForLoadState('networkidle');
    
    // Verify page title
    await expect(page.locator('text=Review readiness')).toBeVisible();
    
    // Verify case number displayed
    await expect(page.locator('text=CS-002')).toBeVisible();
  });

  test('should display readiness checklist', async ({ page }) => {
    await page.goto('/cases/case-CS-002/handoff');
    await page.waitForLoadState('networkidle');
    
    // Should show readiness checklist
    await expect(page.locator('h2:has-text("Readiness checklist")')).toBeVisible();
    
    // Should show completion badge
    await expect(page.locator('text=/\\d+ of \\d+ complete/')).toBeVisible();
    
    // Should show checklist items
    await expect(page.locator('text=Linked evidence')).toBeVisible();
    await expect(page.locator('text=Investigation notes')).toBeVisible();
  });

  test('should show handoff package preview when ready', async ({ page }) => {
    await page.goto('/cases/case-CS-002/handoff');
    await page.waitForLoadState('networkidle');
    
    // Assert package preview section exists
    const packagePreview = page.locator('text=Handoff package preview');
    await expect(packagePreview).toBeVisible();
    
    // Verify package contents
    await expect(page.locator('text=What the officer receives')).toBeVisible();
  });

  test('should display four-eyes segregation card', async ({ page }) => {
    await page.goto('/cases/case-CS-002/handoff');
    await page.waitForLoadState('networkidle');
    
    // Should show four-eyes card
    await expect(page.locator('text=Independent review required')).toBeVisible();
    
    // Should show officer selector
    await expect(page.locator('label:has-text("Reviewing officer")')).toBeVisible();
    
    // Should have officer dropdown
    const officerSelect = page.locator('select[id="officer-select"]');
    await expect(officerSelect).toBeVisible();
  });

  test('should allow officer selection', async ({ page }) => {
    await page.goto('/cases/case-CS-002/handoff');
    await page.waitForLoadState('networkidle');
    
    // Select an officer
    const officerSelect = page.locator('select[id="officer-select"]');
    await expect(officerSelect).toBeVisible();
    
    // Get the first option value
    const firstOption = await officerSelect.locator('option').first().getAttribute('value');
    if (firstOption) {
      await officerSelect.selectOption(firstOption);
      
      // Verify selection
      await expect(officerSelect).toHaveValue(firstOption);
    }
  });

  test('should submit handoff when ready', async ({ page }) => {
    await page.goto('/cases/case-CS-002/handoff');
    await page.waitForLoadState('networkidle');
    
    // Assert share button exists and is enabled
    const shareButton = page.locator('button:has-text("Share for officer review")');
    await expect(shareButton).toBeVisible();
    await expect(shareButton).toBeEnabled();
    
    // Click share button
    await shareButton.click();
    
    // Should show confirmation dialog
    await expect(page.locator('text=/Share .* with/')).toBeVisible();
    
    // Confirm
    await page.click('button:has-text("Share")');
    
    // Should navigate away or show success
    await page.waitForURL(/\/alerts|\/cases/, { timeout: 10000 });
  });

  test('should show blocker when case not ready', async ({ page }) => {
    // case-CS-001 has open requests, should not be ready
    await page.goto('/cases/case-CS-001/handoff');
    await page.waitForLoadState('networkidle');
    
    // Assert unresolved section exists
    const unresolvedSection = page.locator('text=Unresolved issues');
    await expect(unresolvedSection).toBeVisible();
    
    // Should show issues
    const hasIssues = await page.locator('text=/IR-|incomplete/').isVisible();
    if (hasIssues) {
      // Share button should be disabled
      await expect(page.locator('button:has-text("Share for officer review")')).toBeDisabled();
    }
  });
});
