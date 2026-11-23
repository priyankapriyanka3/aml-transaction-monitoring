/**
 * End-to-end journey test for complete Flow 01 workflow.
 * 
 * Tests the full investigator-to-officer journey:
 * 1. Login as investigator Riya
 * 2. Search and assign alert AL-1042
 * 3. View evidence with rule snapshots
 * 4. Create case CS-204
 * 5. Add narrative note
 * 6. Identify evidence gap and create information request IR-012
 * 7. Record response to request
 * 8. Verify readiness checklist
 * 9. Assign officer Morgan
 * 10. Share for review
 * 11. Logout investigator
 * 12. Login as officer Morgan
 * 13. Review package
 * 14. Select outcome FALSE_POSITIVE
 * 15. Enter rationale
 * 16. Record decision
 * 17. Verify immutable decision record
 */

import { test, expect } from './_pipeline_guard';

test.describe('Full Flow 01 Journey', () => {
  
  test('Complete investigator-to-officer workflow with decision recording', async ({ page }) => {
    // Step 1: Login as investigator Riya
    await page.goto('/login');
    await page.fill('input[name="email"]', 'investigator@example.com');
    await page.fill('input[name="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    
    // Wait for navigation to alerts page
    await expect(page).toHaveURL(/\/alerts/);
    
    // Step 2: Search and assign alert AL-1042
    // Wait for alert queue to load
    await expect(page.locator('text=AL-1042')).toBeVisible({ timeout: 10000 });
    
    // Click on alert AL-1042 to view details
    const alertCard = page.locator('[data-testid="alert-card-AL-1042"], .alert-queue-card:has-text("AL-1042")').first();
    await alertCard.click();
    
    // Step 3: View evidence with rule snapshots
    await expect(page).toHaveURL(/\/alerts\/.*\/evidence/);
    
    // Verify transaction facts are displayed
    await expect(page.locator('text=Transaction Facts')).toBeVisible();
    await expect(page.locator('text=$150,000.00')).toBeVisible();
    await expect(page.locator('text=USD')).toBeVisible();
    await expect(page.locator('text=GB')).toBeVisible(); // Source country
    await expect(page.locator('text=AE')).toBeVisible(); // Destination country
    
    // Verify rule snapshots section
    await expect(page.locator('text=Rule Evaluation History')).toBeVisible();
    
    // Verify MATCH badge (red) exists
    const matchBadge = page.locator('.badge-match, [data-outcome="MATCH"]').first();
    await expect(matchBadge).toBeVisible();
    await expect(matchBadge).toContainText('MATCH');
    
    // Verify PASS badge (green) exists
    const passBadge = page.locator('.badge-pass, [data-outcome="PASS"]').first();
    await expect(passBadge).toBeVisible();
    await expect(passBadge).toContainText('PASS');
    
    // Verify rule version displayed (e.g., "v3.2")
    await expect(page.locator('text=/v\\d+\\.\\d+/')).toBeVisible();
    
    // Step 4: Create case CS-204
    await page.click('button:has-text("Create case"), button:has-text("Create Case")');
    
    // Wait for case creation success
    await expect(page.locator('text=/Case CS-\\d+ created/')).toBeVisible({ timeout: 5000 });
    
    // Navigate to case investigation page
    await expect(page).toHaveURL(/\/cases\/.*\/investigation/);
    
    // Step 5: Add narrative note
    const noteTextarea = page.locator('textarea[name="note_text"], textarea[placeholder*="note"], textarea[placeholder*="investigation"]').first();
    await noteTextarea.fill('Customer profile indicates legitimate business operations. Transaction aligns with expected activity pattern based on historical data.');
    
    const addNoteButton = page.locator('button:has-text("Add note"), button:has-text("Save note")').first();
    await addNoteButton.click();
    
    // Verify note added successfully
    await expect(page.locator('text=Customer profile indicates legitimate')).toBeVisible({ timeout: 5000 });
    
    // Step 6: Identify evidence gap and create information request
    // Navigate to requests section or click create request button
    const createRequestButton = page.locator('button:has-text("Create request"), button:has-text("New request"), button:has-text("Add request")').first();
    
    if (await createRequestButton.isVisible()) {
      await createRequestButton.click();
    } else {
      // Try navigation approach
      const requestsTab = page.locator('text=Requests, text=Information Requests').first();
      if (await requestsTab.isVisible()) {
        await requestsTab.click();
        await page.click('button:has-text("Create request"), button:has-text("New request")');
      }
    }
    
    // Fill information request form
    await page.fill('input[name="gap_title"], input[placeholder*="title"]', 'Source of Funds Verification');
    await page.fill('textarea[name="gap_description"], textarea[placeholder*="description"]', 'Need documentation showing source of the $150,000 transfer');
    await page.fill('input[name="target_party"], input[placeholder*="target"]', 'Customer Operations Team');
    await page.fill('input[name="delivery_channel"], input[placeholder*="channel"]', 'Internal ticket system');
    await page.fill('textarea[name="reason_text"], textarea[placeholder*="reason"]', 'Verify legitimacy of large cross-border transfer');
    
    // Set due date (3 days from now)
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 3);
    const dueDateStr = dueDate.toISOString().split('T')[0];
    await page.fill('input[type="date"], input[name="due_at_utc"]', dueDateStr);
    
    // Submit request
    await page.click('button[type="submit"], button:has-text("Create"), button:has-text("Submit")');
    
    // Verify request created
    await expect(page.locator('text=Source of Funds Verification')).toBeVisible({ timeout: 5000 });
    
    // Step 7: Record response to request
    // Click on the request to view details
    await page.click('text=Source of Funds Verification');
    
    // Fill response form
    const responseSummary = page.locator('textarea[name="response_summary"], textarea[placeholder*="response"]').first();
    await responseSummary.fill('Customer operations supplied source-of-funds documents showing legitimate business revenue from international contracts.');
    
    // Set received date
    const receivedDate = new Date().toISOString().split('T')[0];
    await page.fill('input[name="received_at_utc"], input[type="date"]', receivedDate);
    
    // Submit response
    await page.click('button:has-text("Record response"), button:has-text("Submit response")');
    
    // Verify response recorded
    await expect(page.locator('text=Response recorded')).toBeVisible({ timeout: 5000 });
    
    // Step 8: Verify readiness checklist
    // Navigate to readiness page
    await page.goto(`${page.url().split('/requests')[0]}/readiness`);
    
    // Verify all checklist items are complete
    const checklistItems = page.locator('[data-testid="checklist-item"], .checklist-item');
    const itemCount = await checklistItems.count();
    
    for (let i = 0; i < itemCount; i++) {
      const item = checklistItems.nth(i);
      const completeIndicator = item.locator('.checkmark, [data-complete="true"], .complete-icon, text=✓');
      await expect(completeIndicator).toBeVisible();
    }
    
    // Step 9: Assign officer Morgan
    const officerDropdown = page.locator('select[name="officer_user_id"], select[id="officer-select"]').first();
    await officerDropdown.selectOption({ label: /Morgan.*Lee|Officer/ });
    
    // Verify assignment confirmation
    await expect(page.locator('text=Officer assigned')).toBeVisible({ timeout: 5000 });
    
    // Step 10: Share for review
    const shareButton = page.locator('button:has-text("Share for review"), button:has-text("Share case")').first();
    await shareButton.click();
    
    // Verify share success
    await expect(page.locator('text=Case shared for review')).toBeVisible({ timeout: 5000 });
    
    // Step 11: Logout investigator
    await page.click('button:has-text("Logout"), button:has-text("Log out"), [aria-label="Logout"]');
    await expect(page).toHaveURL(/\/login/);
    
    // Step 12: Login as officer Morgan
    await page.fill('input[name="email"]', 'officer@example.com');
    await page.fill('input[name="password"]', 'officer123');
    await page.click('button[type="submit"]');
    
    // Wait for login
    await page.waitForURL(/\/(alerts|cases)/);
    
    // Step 13: Review package
    // Navigate to cases list
    await page.goto('/cases');
    
    // Find and click on the case
    await page.click('text=/CS-\\d+/');
    
    // Navigate to officer review
    await page.goto(`${page.url()}/officer-review`);
    
    // Verify review package loaded
    await expect(page.locator('text=Executive Summary, text=Officer Review')).toBeVisible();
    
    // Verify no blockers
    const blockerBanner = page.locator('.blocker-banner, [data-blocker="true"]');
    if (await blockerBanner.isVisible()) {
      await expect(blockerBanner).toContainText(/No blockers|Ready for decision/);
    }
    
    // Step 14: Select outcome FALSE_POSITIVE
    const falsePositiveOption = page.locator('input[value="FALSE_POSITIVE"], label:has-text("False positive"), label:has-text("Close as false positive")').first();
    await falsePositiveOption.click();
    
    // Step 15: Enter rationale
    const rationaleField = page.locator('textarea[name="rationale_text"], textarea[name="rationale"], textarea[placeholder*="rationale"]').first();
    await rationaleField.fill('Transaction is legitimate business activity with verified source of funds. Customer profile and supporting documentation confirm no AML risk. All evidence supports standard international business transaction.');
    
    // Verify outcome preview shows
    await expect(page.locator('text=/Status:.*FALSE_POSITIVE|Status:.*False Positive/')).toBeVisible();
    
    // Step 16: Record decision
    const recordButton = page.locator('button:has-text("Record decision"), button:has-text("Submit decision")').first();
    await expect(recordButton).toBeEnabled();
    await recordButton.click();
    
    // Step 17: Verify immutable decision record
    // Wait for success message
    await expect(page.locator('text=Decision recorded, text=Decision submitted')).toBeVisible({ timeout: 5000 });
    
    // Verify redirected to cases list or decision confirmation
    await page.waitForURL(/\/(cases|decisions)/);
    
    // Verify case status updated
    await expect(page.locator('text=Approved, text=FALSE_POSITIVE, text=False Positive')).toBeVisible();
  });
  
  test('Readiness checklist shows all required items', async ({ page }) => {
    // Login as investigator
    await page.goto('/login');
    await page.fill('input[name="email"]', 'investigator@example.com');
    await page.fill('input[name="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/alerts/);
    
    // Navigate to an existing case readiness page
    await page.goto('/cases');
    const caseLink = page.locator('text=/CS-\\d+/').first();
    await caseLink.click();
    
    await page.goto(`${page.url()}/readiness`);
    
    // Verify 4 required checklist items exist
    await expect(page.locator('text=Linked evidence, text=linked_evidence')).toBeVisible();
    await expect(page.locator('text=Investigation notes, text=investigation_notes')).toBeVisible();
    await expect(page.locator('text=Responses reviewed, text=responses_reviewed')).toBeVisible();
    await expect(page.locator('text=No open requests, text=no_open_requests')).toBeVisible();
    
    // Verify package summary section
    await expect(page.locator('text=Package Summary, text=Review Package')).toBeVisible();
    await expect(page.locator('text=/\\d+ alert/i')).toBeVisible();
    await expect(page.locator('text=/\\d+ note/i')).toBeVisible();
  });
  
  test('Four-eyes enforcement prevents self-assignment', async ({ page }) => {
    // Login as investigator
    await page.goto('/login');
    await page.fill('input[name="email"]', 'investigator@example.com');
    await page.fill('input[name="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/alerts/);
    
    // Navigate to readiness page of a case created by this investigator
    await page.goto('/cases');
    const caseLink = page.locator('text=/CS-20\\d/').first();
    await caseLink.click();
    
    await page.goto(`${page.url()}/readiness`);
    
    // Verify officer dropdown does NOT contain investigator's own name
    const officerDropdown = page.locator('select[name="officer_user_id"], select[id="officer-select"]').first();
    const options = await officerDropdown.locator('option').allTextContents();
    
    // Should not contain "Riya" (the logged-in investigator)
    const hasInvestigatorName = options.some(opt => opt.includes('Riya') || opt.includes('Sharma'));
    expect(hasInvestigatorName).toBe(false);
    
    // Should contain officer names like "Morgan"
    const hasOfficerName = options.some(opt => opt.includes('Morgan') || opt.includes('Officer'));
    expect(hasOfficerName).toBe(true);
  });
  
  test('Evidence displays complete transaction context', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="email"]', 'investigator@example.com');
    await page.fill('input[name="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/alerts/);
    
    // Navigate to alert evidence
    await page.click('text=AL-1042');
    await expect(page).toHaveURL(/\/evidence/);
    
    // Verify all transaction context fields displayed
    await expect(page.locator('text=Transaction Facts, text=Evidence')).toBeVisible();
    
    // Amount
    await expect(page.locator('text=/\\$150,000|150000/')).toBeVisible();
    
    // Currency
    await expect(page.locator('text=USD')).toBeVisible();
    
    // Customer name
    await expect(page.locator('text=Acme Corp, text=Customer')).toBeVisible();
    
    // Account reference
    await expect(page.locator('text=/ACC-\\d+/')).toBeVisible();
    
    // Corridor (GB → AE)
    await expect(page.locator('text=GB')).toBeVisible();
    await expect(page.locator('text=AE')).toBeVisible();
    
    // Date/time
    await expect(page.locator('text=/2026|Nov|November/')).toBeVisible();
  });
  
  test('Rule snapshots display with version and outcome badges', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="email"]', 'investigator@example.com');
    await page.fill('input[name="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/alerts/);
    
    // Navigate to alert evidence
    await page.click('text=AL-1042');
    await expect(page).toHaveURL(/\/evidence/);
    
    // Verify rule snapshots section
    await expect(page.locator('text=Rule Evaluation, text=Historical Rules')).toBeVisible();
    
    // Verify at least 2 rule snapshots present
    const ruleRows = page.locator('[data-testid="rule-snapshot"], .rule-outcome-row');
    await expect(ruleRows.first()).toBeVisible();
    
    const ruleCount = await ruleRows.count();
    expect(ruleCount).toBeGreaterThanOrEqual(2);
    
    // Verify version strings (e.g., "v3.2")
    const versionText = page.locator('text=/v\\d+\\.\\d+/').first();
    await expect(versionText).toBeVisible();
    
    // Verify MATCH badge styling (should be red/critical)
    const matchBadge = page.locator('[data-outcome="MATCH"], .badge-match').first();
    await expect(matchBadge).toBeVisible();
    
    // Verify PASS badge styling (should be green/success)
    const passBadge = page.locator('[data-outcome="PASS"], .badge-pass').first();
    await expect(passBadge).toBeVisible();
    
    // Verify summary line
    await expect(page.locator('text=/\\d+ rules matched|Snapshots are stored/')).toBeVisible();
  });
});
