import { test, expect } from './_pipeline_guard';

/**
 * E2E Journey Test: Information Request Issuance → Response Recording → Recommendation Unblocked → Handoff Submission
 * 
 * This test simulates a complete investigator workflow with information requests:
 * 1. Login as investigator (riya)
 * 2. Navigate to an existing case (CS-001 from seed)
 * 3. Issue an information request
 * 4. Verify case transitions to PENDING_INFORMATION
 * 5. Record a response to the information request
 * 6. Verify case returns to INVESTIGATING status
 * 7. Submit recommendation (now unblocked)
 * 8. Navigate to handoff page and submit handoff
 * 9. Verify case transitions to SUBMITTED_FOR_REVIEW
 */
test.describe('Journey: Information Request → Response → Recommendation → Handoff', () => {
  test('should complete workflow with information request blocking and unblocking recommendation', async ({ page }) => {
    // ===== Step 1: Login =====
    await page.goto('/login');
    await page.fill('input[name="username"]', 'riya');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/alerts', { timeout: 10000 });
    await page.waitForLoadState('networkidle');

    console.log('✓ Step 1: Logged in as investigator');

    // ===== Step 2: Navigate to Existing Case =====
    // Use seed case CS-001 which should exist
    await page.goto('/cases/CS-001');
    await page.waitForLoadState('networkidle');

    // Verify case loaded
    await expect(page.locator('text=/Case CS-001/')).toBeVisible({ timeout: 5000 });

    console.log('✓ Step 2: Navigated to case CS-001');

    // ===== Step 3: Navigate to Information Requests Section =====
    // Look for information requests tab or navigation
    const infoRequestsLink = page.locator('a, button', { hasText: /Information.*request|Requests/i });
    await expect(infoRequestsLink).toBeVisible({ timeout: 5000 });
    await infoRequestsLink.click();
    await page.waitForTimeout(1000);

    console.log('✓ Step 3: Navigated to information requests section');

    // ===== Step 4: Issue New Information Request =====
    const newRequestButton = page.locator('button', { hasText: /New.*request|Create.*request|Issue.*request/i });
    await expect(newRequestButton).toBeVisible({ timeout: 5000 });
    await newRequestButton.click();

    await page.waitForTimeout(1000);

    // Fill information request form
    // Requested summary
    const requestedSummary = page.locator('textarea#requested-summary, textarea[name="requested-summary"], textarea').first();
    await expect(requestedSummary).toBeVisible({ timeout: 5000 });
    await requestedSummary.fill('Request detailed transaction receipts and counterparty identification documents for all transfers exceeding $200,000 in the past 90 days.');

    // Rationale
    const rationale = page.locator('textarea#rationale, textarea[name="rationale"], textarea').nth(1);
    await expect(rationale).toBeVisible();
    await rationale.fill('Additional documentation required to verify legitimacy of high-value cross-border transactions and establish beneficial ownership of receiving entities.');

    // Due date (set to 7 days from now)
    const dueDate = page.locator('input[type="date"]#due-date, input[type="date"][name="due-date"], input[type="date"]');
    await expect(dueDate).toBeVisible();
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 7);
    const dateString = futureDate.toISOString().split('T')[0];
    await dueDate.fill(dateString);

    // Submit request
    const submitRequestButton = page.locator('button', { hasText: /Submit.*request|Send.*request|Create.*request/i });
    await expect(submitRequestButton).toBeVisible();
    await submitRequestButton.click();

    await page.waitForTimeout(3000);
    console.log('✓ Step 4: Information request issued');

    // ===== Step 5: Verify Case Transitioned to PENDING_INFORMATION =====
    // Navigate back to case overview
    await page.goto('/cases/CS-001');
    await page.waitForLoadState('networkidle');

    // Check status
    await expect(page.locator('text=/Status.*PENDING.*INFORMATION/i')).toBeVisible({ timeout: 5000 });

    console.log('✓ Step 5: Case status transitioned to PENDING_INFORMATION');

    // ===== Step 6: Navigate Back to Information Requests and Record Response =====
    await page.goto('/cases/CS-001/information-requests');
    await page.waitForLoadState('networkidle');

    // Find the open request
    const openRequest = page.locator('article, div').filter({ hasText: /Request detailed transaction receipts/ }).first();
    await expect(openRequest).toBeVisible({ timeout: 5000 });

    // Click "Record response" or similar button
    const recordResponseButton = openRequest.locator('button', { hasText: /Record.*response|Add.*response|Respond/i });
    await expect(recordResponseButton).toBeVisible({ timeout: 5000 });
    await recordResponseButton.click();

    await page.waitForTimeout(1000);

    // Fill response summary
    const responseSummary = page.locator('textarea#response-summary, textarea[name="response-summary"], textarea').first();
    await expect(responseSummary).toBeVisible({ timeout: 5000 });
    await responseSummary.fill('Customer provided complete transaction receipts and certified beneficial ownership documents. All counterparties identified with valid business registrations. Documentation verified and attached to case file.');

    // Submit response
    const submitResponseButton = page.locator('button', { hasText: /Submit.*response|Record.*response|Save.*response/i });
    await expect(submitResponseButton).toBeVisible();
    await submitResponseButton.click();

    await page.waitForTimeout(3000);
    console.log('✓ Step 6: Response recorded for information request');

    // ===== Step 7: Verify Case Returned to INVESTIGATING Status =====
    await page.goto('/cases/CS-001');
    await page.waitForLoadState('networkidle');

    // Check status returned to INVESTIGATING
    await expect(page.locator('text=/Status.*INVESTIGATING/i')).toBeVisible({ timeout: 5000 });

    console.log('✓ Step 7: Case status returned to INVESTIGATING (unblocked)');

    // ===== Step 8: Submit Recommendation (Now Unblocked) =====
    // Scroll to recommendation section
    const recommendationSection = page.locator('text=/Submit.*recommendation|Recommendation/i').first();
    await expect(recommendationSection).toBeVisible({ timeout: 5000 });

    // Select recommendation outcome
    const substantiateOption = page.locator('[role="radio"]', { hasText: /Substantiate|No.*further.*action|Escalate/i }).first();
    await expect(substantiateOption).toBeVisible({ timeout: 5000 });
    await substantiateOption.click();

    // Fill findings summary
    const findingsSummary = page.locator('textarea#findings-summary, textarea[name="findings-summary"], textarea').last();
    await expect(findingsSummary).toBeVisible();
    await findingsSummary.fill('Following receipt of additional documentation, investigation reveals all transactions have legitimate business purpose with properly documented counterparties. Customer cooperation was excellent. Recommend no further action required.');

    // Submit recommendation
    const submitRecommendationButton = page.locator('button', { hasText: /Submit.*recommendation/i });
    await expect(submitRecommendationButton).toBeVisible();
    await expect(submitRecommendationButton).toBeEnabled();
    await submitRecommendationButton.click();

    await page.waitForTimeout(3000);
    console.log('✓ Step 8: Recommendation submitted');

    // ===== Step 9: Navigate to Handoff Page =====
    // Look for handoff/review navigation
    const handoffLink = page.locator('a, button', { hasText: /Handoff|Review|Submit.*review/i });
    await expect(handoffLink).toBeVisible({ timeout: 5000 });
    await handoffLink.click();
    await page.waitForTimeout(1000);

    console.log('✓ Step 9: Navigated to handoff page');

    // ===== Step 10: Verify Readiness Checklist =====
    // Check for readiness checklist or readiness indicators
    const readinessChecklist = page.locator('text=/Readiness|Checklist|Complete/i');
    await expect(readinessChecklist).toBeVisible({ timeout: 5000 });
    console.log('  ✓ Readiness checklist displayed');

    // ===== Step 11: Submit Handoff =====
    // Find officer selection or handoff submission
    const submitHandoffButton = page.locator('button', { hasText: /Submit.*handoff|Submit.*review|Send.*review/i });
    await expect(submitHandoffButton).toBeVisible({ timeout: 5000 });

    // If officer selection is required, select one
    const officerSelect = page.locator('select#officer, select[name="officer"]');
    await expect(officerSelect).toBeVisible({ timeout: 5000 });
    await officerSelect.selectOption({ index: 1 }); // Select first available officer

    await submitHandoffButton.click();
    await page.waitForTimeout(3000);

    console.log('✓ Step 11: Handoff submitted');

    // ===== Step 12: Verify Case Transitioned to SUBMITTED_FOR_REVIEW =====
    await page.goto('/cases/CS-001');
    await page.waitForLoadState('networkidle');

    // Check for final status
    await expect(page.locator('text=/Status.*SUBMITTED.*REVIEW|Status.*REVIEW.*READY/i')).toBeVisible({ timeout: 5000 });

    console.log('✓ Step 12: Case status transitioned to SUBMITTED_FOR_REVIEW');

    // ===== Verify Final State =====
    // Verify recommendation is visible
    await expect(page.locator('text=/Recommend.*no.*further.*action|Following receipt of additional documentation/i')).toBeVisible();

    // Verify information request was resolved
    await page.goto('/cases/CS-001/information-requests');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('text=/RESPONDED|Resolved|Closed/i')).toBeVisible({ timeout: 5000 });

    console.log('✅ Journey completed successfully: Info Request → Response → Unblock → Recommendation → Handoff');
  });
});
