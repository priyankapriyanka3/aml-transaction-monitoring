// E2E test for wireframe_04 - Information Requests
import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 04 - Information Requests', () => {
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

  test('should navigate to information requests page', async ({ page }) => {
    // Navigate to a case (case-CS-001 from seed data)
    await page.goto('/cases/case-CS-001/information-requests');
    await page.waitForLoadState('networkidle');
    
    // Verify page title
    await expect(page.locator('text=Information requests')).toBeVisible();
    
    // Verify case number displayed
    await expect(page.locator('text=CS-001')).toBeVisible();
  });

  test('should display existing information requests', async ({ page }) => {
    await page.goto('/cases/case-CS-001/information-requests');
    await page.waitForLoadState('networkidle');
    
    // Should show requests section
    await expect(page.locator('h2:has-text("Requests")')).toBeVisible();
    
    // Should display at least one request (IR-001 and IR-002 exist in seed)
    await expect(page.locator('text=IR-')).toBeVisible();
  });

  test('should show decision blocker banner when requests are open', async ({ page }) => {
    await page.goto('/cases/case-CS-001/information-requests');
    await page.waitForLoadState('networkidle');
    
    // CS-001 has open/overdue requests, should show blocker banner
    await expect(page.locator('text=decision blocked')).toBeVisible();
  });

  test('should open new request form', async ({ page }) => {
    await page.goto('/cases/case-CS-001/information-requests');
    await page.waitForLoadState('networkidle');
    
    // Click new request button
    await page.click('button:has-text("New request")');
    
    // Verify form is visible
    await expect(page.locator('text=New information request')).toBeVisible();
    await expect(page.locator('label:has-text("Information requested")')).toBeVisible();
    await expect(page.locator('label:has-text("Due date")')).toBeVisible();
  });

  test('should record response to open request', async ({ page }) => {
    await page.goto('/cases/case-CS-001/information-requests');
    await page.waitForLoadState('networkidle');
    
    // Find and assert an open request exists
    const openRequest = page.locator('text=/Open · \\d+ day/').first();
    await expect(openRequest).toBeVisible();
    await openRequest.click();
    
    // Fill response form
    await page.fill('textarea[id="response-summary"]', 'All requested documents have been provided via secure portal');
    
    // Set received date (today)
    const today = new Date().toISOString().split('T')[0];
    await page.fill('input[id="received-date"]', today);
    
    // Select channel
    await page.selectOption('select[id="response-channel"]', 'EMAIL');
    
    // Submit response
    await page.click('button:has-text("Record response")');
    
    // Should reload and show success state
    await expect(page.locator('text=RESPONDED')).toBeVisible({ timeout: 10000 });
  });
});
