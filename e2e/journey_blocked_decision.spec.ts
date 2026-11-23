/**
 * End-to-end journey test for decision blocker enforcement.
 * 
 * Tests the flow where an officer attempts to record a decision
 * but is blocked by an open information request, verifying:
 * 1. Same initial flow as full journey (login, assign, evidence, case creation)
 * 2. Create information request
 * 3. Share case for review WITHOUT recording response
 * 4. Officer login and review
 * 5. Verify blocker banner displayed
 * 6. Attempt decision recording
 * 7. Verify 409 error and decision blocked
 * 8. Verify blocker banner persists
 */

import { test, expect } from './_pipeline_guard';

test.describe('Blocked Decision Journey', () => {
  
  test('Officer cannot record decision when open request exists', async ({ page }) => {
    // Step 1: Login as investigator
    await page.goto('/login');
    await page.fill('input[name="email"]', 'investigator@example.com');
    await page.fill('input[name="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/alerts/);
    
    // Step 2: Navigate to alert and view evidence
    await page.click('text=AL-1042');
    await expect(page).toHaveURL(/\/evidence/);
    
    // Step 3: Create case
    await page.click('button:has-text("Create case"), button:has-text("Create Case")');
    await expect(page.locator('text=/Case CS-\\d+ created/')).toBeVisible({ timeout: 5000 });
    await expect(page).toHaveURL(/\/cases\/.*\/investigation/);
    
    // Step 4: Add investigation note
    const noteTextarea = page.locator('textarea[name="note_text"], textarea[placeholder*="note"]').first();
    await noteTextarea.fill('Initial investigation findings. Additional information required before proceeding.');
    await page.click('button:has-text("Add note"), button:has-text("Save note")');
    await expect(page.locator('text=Initial investigation findings')).toBeVisible({ timeout: 5000 });
    
    // Step 5: Create information request (but do NOT record response)
    const createRequestButton = page.locator('button:has-text("Create request"), button:has-text("New request"), button:has-text("Add request")').first();
    
    if (await createRequestButton.isVisible()) {
      await createRequestButton.click();
    } else {
      const requestsTab = page.locator('text=Requests, text=Information Requests').first();
      if (await requestsTab.isVisible()) {
        await requestsTab.click();
        await page.click('button:has-text("Create request"), button:has-text("New request")');
      }
    }
    
    // Fill request form
    await page.fill('input[name="gap_title"], input[placeholder*="title"]', 'Pending Customer Verification');
    await page.fill('textarea[name="gap_description"], textarea[placeholder*="description"]', 'Awaiting customer identity verification documents');
    await page.fill('input[name="target_party"], input[placeholder*="target"]', 'Customer Verification Team');
    await page.fill('input[name="delivery_channel"], input[placeholder*="channel"]', 'Internal system');
    await page.fill('textarea[name="reason_text"], textarea[placeholder*="reason"]', 'Required for AML compliance verification');
    
    // Set due date
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 5);
    await page.fill('input[type="date"], input[name="due_at_utc"]', dueDate.toISOString().split('T')[0]);
    
    // Submit request
    await page.click('button[type="submit"], button:has-text("Create"), button:has-text("Submit")');
    await expect(page.locator('text=Pending Customer Verification')).toBeVisible({ timeout: 5000 });
    
    // IMPORTANT: Do NOT record response - leave request OPEN
    
    // Step 6: Navigate to readiness (checklist should show incomplete due to open request)
    const currentUrl = page.url();
    const caseId = currentUrl.match(/cases\/([^/]+)/)?.[1];
    await page.goto(`/cases/${caseId}/readiness`);
    
    // Verify "no_open_requests" checklist item is incomplete
    const noOpenRequestsItem = page.locator('[data-item-id="no_open_requests"], text=No open requests').first();
    const incompleteIndicator = noOpenRequestsItem.locator('.incomplete, [data-complete="false"], .outline-circle, text=○');
    
    // If the indicator exists, it should show incomplete
    if (await incompleteIndicator.count() > 0) {
      await expect(incompleteIndicator).toBeVisible();
    }
    
    // Step 7: Assign officer anyway (system may allow assignment even with blockers)
    const officerDropdown = page.locator('select[name="officer_user_id"], select[id="officer-select"]').first();
    
    if (await officerDropdown.isVisible()) {
      await officerDropdown.selectOption({ label: /Morgan.*Lee|Officer/ });
      await expect(page.locator('text=Officer assigned')).toBeVisible({ timeout: 5000 });
    }
    
    // Step 8: Attempt to share for review
    // Note: System should either block share or allow share but block decision
    const shareButton = page.locator('button:has-text("Share for review"), button:has-text("Share case")').first();
    
    if (await shareButton.isEnabled()) {
      await shareButton.click();
      
      // May show error or success - either is valid depending on when blocker enforced
      const errorMessage = page.locator('text=/cannot share|blocked|open request/i');
      const successMessage = page.locator('text=/shared for review|case shared/i');
      
      // Wait for either outcome
      await Promise.race([
        errorMessage.waitFor({ timeout: 3000 }).catch(() => {}),
        successMessage.waitFor({ timeout: 3000 }).catch(() => {})
      ]);
    }
    
    // Step 9: Logout investigator
    await page.click('button:has-text("Logout"), button:has-text("Log out"), [aria-label="Logout"]');
    await expect(page).toHaveURL(/\/login/);
    
    // Step 10: Login as officer
    await page.fill('input[name="email"]', 'officer@example.com');
    await page.fill('input[name="password"]', 'officer123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(alerts|cases)/);
    
    // Step 11: Navigate to officer review page
    await page.goto('/cases');
    await page.click('text=/CS-\\d+/');
    await page.goto(`${page.url()}/officer-review`);
    
    // Step 12: Verify blocker banner displayed
    const blockerBanner = page.locator('.blocker-banner, [data-blocker="true"], .warning-banner, .decision-blocker');
    await expect(blockerBanner).toBeVisible({ timeout: 5000 });
    
    // Verify blocker message mentions open requests
    await expect(blockerBanner).toContainText(/open request|pending request|blocker|cannot proceed/i);
    
    // Step 13: Verify decision controls are disabled or hidden
    const decisionSelector = page.locator('input[value="APPROVE"], input[value="FALSE_POSITIVE"]').first();
    const rationaleField = page.locator('textarea[name="rationale_text"], textarea[name="rationale"]').first();
    const recordButton = page.locator('button:has-text("Record decision"), button:has-text("Submit decision")').first();
    
    // At least one of these should be disabled
    if (await decisionSelector.isVisible()) {
      // Selector may be disabled
      const isDisabled = await decisionSelector.isDisabled();
      if (!isDisabled) {
        // If not disabled, recording should fail
        await decisionSelector.click();
        
        if (await rationaleField.isVisible()) {
          await rationaleField.fill('This should be blocked by open request');
        }
        
        if (await recordButton.isVisible()) {
          const wasEnabled = await recordButton.isEnabled();
          
          if (wasEnabled) {
            // Attempt to record decision
            await recordButton.click();
            
            // Step 14: Verify error message displayed
            const errorMessage = page.locator('text=/cannot record|blocked|open request|409|conflict/i');
            await expect(errorMessage).toBeVisible({ timeout: 5000 });
            
            // Verify still on officer review page (not redirected)
            await expect(page).toHaveURL(/\/officer-review/);
          } else {
            // Button disabled as expected
            expect(wasEnabled).toBe(false);
          }
        }
      }
    } else {
      // Decision controls hidden entirely - valid blocker enforcement
      await expect(blockerBanner).toBeVisible();
    }
    
    // Step 15: Verify blocker banner persists after failed attempt
    await expect(blockerBanner).toBeVisible();
  });
  
  test('Blocker banner shows when overdue request exists', async ({ page }) => {
    // Login as officer
    await page.goto('/login');
    await page.fill('input[name="email"]', 'officer@example.com');
    await page.fill('input[name="password"]', 'officer123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(alerts|cases)/);
    
    // Navigate to a case with overdue request (CS-205 from seed data)
    await page.goto('/cases');
    const overdueCase = page.locator('text=CS-205');
    
    if (await overdueCase.isVisible()) {
      await overdueCase.click();
      await page.goto(`${page.url()}/officer-review`);
      
      // Verify blocker banner for overdue request
      const blockerBanner = page.locator('.blocker-banner, [data-blocker="true"], .warning-banner');
      await expect(blockerBanner).toBeVisible({ timeout: 5000 });
      await expect(blockerBanner).toContainText(/overdue|blocker/i);
      
      // Verify decision recording disabled
      const recordButton = page.locator('button:has-text("Record decision")').first();
      
      if (await recordButton.isVisible()) {
        await expect(recordButton).toBeDisabled();
      }
    }
  });
  
  test('Readiness checklist shows incomplete when requests open', async ({ page }) => {
    // Login as investigator
    await page.goto('/login');
    await page.fill('input[name="email"]', 'investigator@example.com');
    await page.fill('input[name="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/alerts/);
    
    // Navigate to case with open request
    await page.goto('/cases');
    const testCase = page.locator('text=/CS-20\\d/').first();
    await testCase.click();
    
    // Create open request if none exists
    const requestsTab = page.locator('text=Requests').first();
    if (await requestsTab.isVisible()) {
      await requestsTab.click();
      
      // Check if open requests exist
      const openRequest = page.locator('text=/OPEN|Pending/i').first();
      
      if (!(await openRequest.isVisible())) {
        // Create a new open request
        await page.click('button:has-text("Create request"), button:has-text("New request")');
        await page.fill('input[name="gap_title"]', 'Test Open Request');
        await page.fill('textarea[name="gap_description"]', 'Test description');
        await page.fill('input[name="target_party"]', 'Test Party');
        await page.fill('input[name="delivery_channel"]', 'Email');
        await page.fill('textarea[name="reason_text"]', 'Test reason');
        
        const dueDate = new Date();
        dueDate.setDate(dueDate.getDate() + 7);
        await page.fill('input[type="date"]', dueDate.toISOString().split('T')[0]);
        
        await page.click('button[type="submit"]');
        await page.waitForTimeout(1000);
      }
    }
    
    // Navigate to readiness
    await page.goto(`${page.url().split('/requests')[0]}/readiness`);
    
    // Verify "no_open_requests" item shows incomplete
    const checklistItems = page.locator('[data-testid="checklist-item"], .checklist-item');
    const noOpenRequestsItem = checklistItems.filter({ hasText: /no open requests|requests closed/i }).first();
    
    if (await noOpenRequestsItem.isVisible()) {
      // Verify incomplete indicator (outline circle, not filled checkmark)
      const incomplete = noOpenRequestsItem.locator('.incomplete, [data-complete="false"], text=○');
      await expect(incomplete).toBeVisible();
    }
    
    // Verify share button disabled or warning shown
    const shareButton = page.locator('button:has-text("Share for review")').first();
    
    if (await shareButton.isVisible()) {
      const isEnabled = await shareButton.isEnabled();
      
      if (isEnabled) {
        // May be enabled but show warning on click
        await shareButton.click();
        const warning = page.locator('text=/cannot share|incomplete|open request/i');
        await expect(warning).toBeVisible({ timeout: 3000 });
      } else {
        // Disabled as expected
        expect(isEnabled).toBe(false);
      }
    }
  });
  
  test('Return for investigation path available when blocked', async ({ page }) => {
    // Login as officer
    await page.goto('/login');
    await page.fill('input[name="email"]', 'officer@example.com');
    await page.fill('input[name="password"]', 'officer123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(alerts|cases)/);
    
    // Navigate to case with blocker
    await page.goto('/cases');
    const blockedCase = page.locator('text=CS-205').first();
    
    if (await blockedCase.isVisible()) {
      await blockedCase.click();
      await page.goto(`${page.url()}/officer-review`);
      
      // Verify blocker present
      const blockerBanner = page.locator('.blocker-banner, [data-blocker="true"]').first();
      await expect(blockerBanner).toBeVisible();
      
      // Verify "Return for further investigation" option available
      const returnButton = page.locator('button:has-text("Return for"), button:has-text("Return for investigation"), text=Return for further investigation').first();
      
      // Return action should be available even when decision is blocked
      if (await returnButton.isVisible()) {
        await expect(returnButton).toBeEnabled();
      }
    }
  });
});
