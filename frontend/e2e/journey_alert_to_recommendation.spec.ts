import { test, expect } from './_pipeline_guard';

/**
 * E2E Journey Test: Alert Triage → Case Creation → Investigation → Recommendation Submission
 * 
 * This test simulates a complete investigator workflow:
 * 1. Login as investigator (riya)
 * 2. Navigate to alert queue
 * 3. Assign an alert and triage it with "INVESTIGATE" outcome
 * 4. Create a case from the alert
 * 5. Navigate to the case workspace
 * 6. Add investigation notes
 * 7. Submit a recommendation
 * 8. Verify the case status transitions to REVIEW_READY
 */
test.describe('Journey: Alert Triage → Case Creation → Investigation → Recommendation', () => {
  test('should complete full investigator workflow from alert to recommendation', async ({ page }) => {
    // ===== Step 1: Login =====
    await page.goto('/login');
    await page.fill('input[name="username"]', 'riya');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/alerts', { timeout: 10000 });
    await page.waitForLoadState('networkidle');

    console.log('✓ Step 1: Logged in as investigator');

    // ===== Step 2: Navigate to Alert Queue and Verify Load =====
    await expect(page.locator('h1', { hasText: 'Alerts' })).toBeVisible();
    await page.waitForSelector('[aria-label="Loading alert queue"], article', { timeout: 10000 });
    await page.waitForSelector('article', { timeout: 10000 });

    console.log('✓ Step 2: Alert queue loaded');

    // ===== Step 3: Assign an Alert =====
    // Find first alert with "Assign to me" button
    const firstAlert = page.locator('article').first();
    await expect(firstAlert).toBeVisible({ timeout: 10000 });

    // Look for an unassigned alert
    const assignButton = page.locator('article').locator('button', { hasText: 'Assign to me' }).first();
    await expect(assignButton).toBeVisible({ timeout: 10000 });
    await assignButton.click();

    await page.waitForTimeout(2000); // Wait for assignment to complete and reload
    console.log('✓ Step 3: Alert assigned');

    // ===== Step 4: Triage Alert with "INVESTIGATE" Outcome =====
    // After reload, find the first alert with a "Triage" button (the one we just assigned)
    await page.waitForLoadState('networkidle');
    const assignedAlertWithTriage = page.locator('article', { has: page.locator('button', { hasText: 'Triage' }) }).first();
    const triageButton = assignedAlertWithTriage.locator('button', { hasText: 'Triage' });
    await expect(triageButton).toBeVisible();
    await triageButton.click();

    // Wait for triage modal
    await expect(page.locator('[role="dialog"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=/Triage alert/')).toBeVisible();

    // Select "INVESTIGATE" outcome (first radio button)
    const investigateOption = page.locator('[role="radio"]').first();
    await expect(investigateOption).toBeVisible();
    await investigateOption.click();

    // Fill rationale
    const rationaleField = page.locator('textarea#rationale');
    await expect(rationaleField).toBeVisible();
    await rationaleField.fill('High-risk cross-border transaction requires detailed investigation. Multiple rules triggered indicating suspicious pattern.');

    // Save disposition
    const saveButton = page.locator('button', { hasText: 'Save disposition' });
    await expect(saveButton).toBeVisible();
    await saveButton.click();

    // Wait for modal to close and page to reload
    await page.waitForTimeout(3000);
    await page.waitForLoadState('networkidle');
    console.log('✓ Step 4: Alert triaged with INVESTIGATE outcome');

    // ===== Step 5: Create Case from Alert =====
    // After triage and reload, find the first alert with "Create case" button
    const triagedAlertWithCreateCase = page.locator('article', { has: page.locator('button', { hasText: 'Create case' }) }).first();
    const createCaseButton = triagedAlertWithCreateCase.locator('button', { hasText: 'Create case' });
    await expect(createCaseButton).toBeVisible({ timeout: 5000 });
    await expect(createCaseButton).toBeEnabled();
    await createCaseButton.click();

    // Wait for navigation to case workspace
    await page.waitForURL(/\/cases\/CS-\d+/, { timeout: 10000 });
    await page.waitForLoadState('networkidle');

    console.log('✓ Step 5: Case created and navigated to case workspace');

    // ===== Step 6: Verify Case Overview Loaded =====
    await expect(page.locator('text=/Case CS-\\d+/')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=/Status.*INVESTIGATING/i')).toBeVisible();

    console.log('✓ Step 6: Case overview loaded with INVESTIGATING status');

    // ===== Step 7: Add Investigation Notes =====
    // Find note textarea
    const noteTextarea = page.locator('textarea').first();
    await expect(noteTextarea).toBeVisible({ timeout: 5000 });
    
    await noteTextarea.fill('Initial investigation commenced. Reviewed transaction history and customer risk profile. Multiple high-value cross-border transfers identified. Further analysis required on counterparty relationships.');

    // Save note
    const saveNoteButton = page.locator('button', { hasText: /Save note|Submit note/i });
    await expect(saveNoteButton).toBeVisible();
    await saveNoteButton.click();

    await page.waitForTimeout(2000);
    console.log('✓ Step 7: Investigation note added');

    // Verify note appears in the case
    await expect(page.locator('text=/Initial investigation commenced/')).toBeVisible({ timeout: 5000 });

    // ===== Step 8: Submit Recommendation =====
    // Scroll to or find the recommendation section
    const recommendationSection = page.locator('text=/Submit.*recommendation|Recommendation/i').first();
    await expect(recommendationSection).toBeVisible({ timeout: 5000 });

    // Select recommendation outcome
    const substantiateOption = page.locator('[role="radio"]', { hasText: /Substantiate|File.*SAR|Escalate/i }).first();
    await expect(substantiateOption).toBeVisible({ timeout: 5000 });
    await substantiateOption.click();

    // Fill findings summary
    const findingsSummary = page.locator('textarea#findings-summary, textarea[name="findings-summary"], textarea').last();
    await expect(findingsSummary).toBeVisible();
    await findingsSummary.fill('Based on investigation, transaction pattern indicates potential money laundering activity. Customer engaged in multiple high-value cross-border transfers with sanctioned jurisdiction connections. Recommend filing SAR and escalating to compliance officer for review.');

    // Submit recommendation
    const submitRecommendationButton = page.locator('button', { hasText: /Submit.*recommendation/i });
    await expect(submitRecommendationButton).toBeVisible();
    await expect(submitRecommendationButton).toBeEnabled();
    await submitRecommendationButton.click();

    await page.waitForTimeout(3000);
    console.log('✓ Step 8: Recommendation submitted');

    // ===== Step 9: Verify Case Status Transitions to REVIEW_READY =====
    // After recommendation submission, the case should transition to REVIEW_READY
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Check for REVIEW_READY or SUBMITTED status
    await expect(page.locator('text=/Status.*REVIEW.*READY|Status.*SUBMITTED/i')).toBeVisible({ timeout: 5000 });

    console.log('✓ Step 9: Case status transitioned to REVIEW_READY');

    // ===== Verify Final State =====
    // Verify recommendation outcome is displayed
    await expect(page.locator('text=/Substantiate|File.*SAR|Escalate/i')).toBeVisible();
    
    // Verify findings summary is displayed
    await expect(page.locator('text=/Based on investigation/')).toBeVisible();

    console.log('✅ Journey completed successfully: Alert → Triage → Case → Investigation → Recommendation');
  });
});
