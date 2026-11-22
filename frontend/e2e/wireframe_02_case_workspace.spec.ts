import { test, expect } from './_pipeline_guard';

test.describe('Wireframe 02: Case Workspace', () => {
  let testCaseId: string;

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
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to case workspace from case link', async ({ page }) => {
    // Wait for alerts to load
    await page.waitForSelector('[aria-label="Loading alert queue"], article', { timeout: 10000 });
    await page.waitForSelector('article', { timeout: 10000 });

    // Get hero alert card
    const heroCard = page.locator('article').first();
    await expect(heroCard).toBeVisible();

    // Assign if needed
    const assignBtn = heroCard.locator('button', { hasText: 'Assign to me' });
    const isAssignVisible = await assignBtn.isVisible();
    if (isAssignVisible) {
      await assignBtn.click();
      await page.waitForTimeout(2000);
    }

    // Create case
    const createCaseBtn = heroCard.locator('button', { hasText: 'Create case' });
    await expect(createCaseBtn).toBeVisible();
    await createCaseBtn.click();

    // Wait for navigation to case page
    await page.waitForURL(/\/cases\/.+/, { timeout: 10000 });

    // Verify case workspace loaded
    await expect(page.locator('h1')).toContainText('CS-');
    await expect(page.locator('text=/Case workspace/i')).toBeVisible();
  });

  test('should display case overview with metadata', async ({ page }) => {
    // Navigate to a known case from seed (CS-001)
    await page.goto('/cases/CS-001');
    await page.waitForLoadState('networkidle');

    // Verify case header
    await expect(page.locator('h1')).toContainText('CS-');
    
    // Verify case summary section
    await expect(page.locator('text=/Case summary/i')).toBeVisible();
    
    // Verify status badge
    await expect(page.locator('text=/Investigating|Under review|Pending/i').first()).toBeVisible();
    
    // Verify linked alerts section
    await expect(page.locator('text=/Linked alert/i')).toBeVisible();
  });

  test('should save investigation note', async ({ page }) => {
    // Navigate to a known case
    await page.goto('/cases/CS-001');
    await page.waitForLoadState('networkidle');

    // Wait for page to load
    await expect(page.locator('h1')).toContainText('CS-', { timeout: 10000 });

    // Find investigation notes section
    await expect(page.locator('text=/Investigation notes/i')).toBeVisible();

    // Find note textarea
    const noteTextarea = page.locator('textarea').first();
    await expect(noteTextarea).toBeVisible();

    // Clear and enter new note
    await noteTextarea.clear();
    await noteTextarea.fill('Test investigation note added via E2E test with sufficient detail for validation.');

    // Click save note button
    const saveNoteBtn = page.locator('button', { hasText: /Save note/i }).first();
    await expect(saveNoteBtn).toBeVisible();
    await saveNoteBtn.click();

    // Wait for save to complete
    await page.waitForTimeout(2000);

    // Verify success (note should appear in list or success message)
    await expect(page.locator('text=/Test investigation note|Note saved|saved successfully/i')).toBeVisible({ timeout: 5000 });
  });

  test('should submit recommendation', async ({ page }) => {
    // Navigate to a known case
    await page.goto('/cases/CS-001');
    await page.waitForLoadState('networkidle');

    // Wait for page to load
    await expect(page.locator('h1')).toContainText('CS-', { timeout: 10000 });

    // Scroll to recommendation section
    const recommendationSection = page.locator('text=/Investigator recommendation|Recommendation/i').first();
    await expect(recommendationSection).toBeVisible({ timeout: 10000 });
    await recommendationSection.scrollIntoViewIfNeeded();

    // Select a recommendation outcome (first radio button)
    const firstRadio = page.locator('[role="radio"]').first();
    await expect(firstRadio).toBeVisible();
    await firstRadio.click();

    // Fill findings summary
    const findingsTextarea = page.locator('textarea#findings, textarea[aria-label*="findings" i], textarea[placeholder*="findings" i]').first();
    await expect(findingsTextarea).toBeVisible({ timeout: 5000 });
    await findingsTextarea.clear();
    await findingsTextarea.fill('Detailed findings summary explaining the investigation outcome with sufficient detail to meet the minimum character requirement for submission validation.');

    // Submit recommendation
    const submitBtn = page.locator('button', { hasText: /Submit recommendation/i }).first();
    await expect(submitBtn).toBeVisible();
    await submitBtn.click();

    // Wait for submission
    await page.waitForTimeout(2000);

    // Verify success (either navigation or message)
    await expect(page.locator('text=/submitted|success|review/i')).toBeVisible({ timeout: 5000 });
  });

  test('should display case activity timeline', async ({ page }) => {
    // Navigate to a known case
    await page.goto('/cases/CS-001');
    await page.waitForLoadState('networkidle');

    // Wait for page to load
    await expect(page.locator('h1')).toContainText('CS-', { timeout: 10000 });

    // Look for activity section
    const activitySection = page.locator('text=/Recent activity|Activity/i');
    await expect(activitySection).toBeVisible({ timeout: 5000 });
    
    // Verify activity timeline has entries
    await expect(page.locator('text=/Case created|Note saved|created from/i')).toBeVisible();
  });
});
