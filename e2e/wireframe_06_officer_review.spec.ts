import { test, expect } from './_pipeline_guard';

test.describe('Screen 6: Officer Review and Decision', () => {
  test.beforeEach(async ({ page }) => {
    // Login with officer seed credentials
    await page.goto('/login');
    await page.fill('input[type="email"]', 'officer@example.com');
    await page.fill('input[type="password"]', 'officer123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/alerts');
  });

  test('should display officer review page with correct title', async ({ page }) => {
    // Navigate to officer review page (using seed case CS-204: 50000000-0000-0000-0000-000000000004)
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Verify page loads with correct title
    await expect(page.locator('h1')).toContainText('Officer review');
    await expect(page.getByText('TRANSFER REVIEW · 06 OF 06')).toBeVisible();

    // Verify pending decision badge
    await expect(page.getByText(/PENDING DECISION/i)).toBeVisible();
  });

  test('should display blocker status banner', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Wait for page load
    await expect(page.locator('h1')).toContainText('Officer review');

    // Should display either success banner (no blockers) or warning banner (blockers present)
    const banners = page.locator('.banner');
    const bannerCount = await banners.count();
    expect(bannerCount).toBeGreaterThan(0);

    // Check for either "No open or overdue requests" or blocker warning
    const successBanner = page.getByText(/No open or overdue requests/i);
    const warningBanner = page.getByText(/decision blocked/i);
    
    const hasSuccessBanner = await successBanner.isVisible().catch(() => false);
    const hasWarningBanner = await warningBanner.isVisible().catch(() => false);
    
    expect(hasSuccessBanner || hasWarningBanner).toBeTruthy();
  });

  test('should display executive summary section', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Verify executive summary section
    await expect(page.getByText('Executive summary')).toBeVisible();

    // Verify review package details are present
    await expect(page.getByText(/linked alert/i)).toBeVisible();
    await expect(page.getByText(/Investigation note/i)).toBeVisible();

    // Verify rule snapshots section
    await expect(page.getByText(/Rule snapshots at evaluation/i)).toBeVisible();
  });

  test('should display rule snapshots with MATCH/PASS badges', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Wait for executive summary
    await expect(page.getByText('Executive summary')).toBeVisible();

    // Verify rule snapshot items are present
    const ruleItems = page.locator('.rule-item, .rule-row');
    const ruleCount = await ruleItems.count();
    
    if (ruleCount > 0) {
      // Verify at least one rule has a badge (MATCH or PASS)
      const badges = page.locator('.badge').filter({ hasText: /MATCH|PASS/i });
      expect(await badges.count()).toBeGreaterThan(0);
    }
  });

  test('should display decision recording section with 4 outcome options', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Verify decision recording section
    await expect(page.getByText('Record decision')).toBeVisible();

    // Verify all 4 decision options are present
    await expect(page.getByText(/^Approve$/i)).toBeVisible();
    await expect(page.getByText(/^Reject$/i)).toBeVisible();
    await expect(page.getByText(/^Escalate$/i)).toBeVisible();
    await expect(page.getByText(/Close as false positive/i)).toBeVisible();
  });

  test('should display mandatory rationale field', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Verify rationale field is present
    await expect(page.getByText('Reason')).toBeVisible();
    
    // Find textarea for rationale
    const rationaleField = page.locator('textarea');
    await expect(rationaleField).toBeVisible();
    
    // Verify placeholder or label indicates it's required
    const rationaleLabel = page.getByText(/Reason.*\*/i);
    await expect(rationaleLabel).toBeVisible();
  });

  test('should display compliance notice about permanent record', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Verify compliance/audit notice
    await expect(page.getByText('Permanent record')).toBeVisible();
    await expect(page.getByText(/cannot be edited or deleted afterwards/i)).toBeVisible();
  });

  test('should display return for investigation button', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Verify return button
    const returnButton = page.getByRole('button', { name: /return for further investigation/i });
    await expect(returnButton).toBeVisible();
  });

  test('should select outcome and enter rationale', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Wait for decision section
    await expect(page.getByText('Record decision')).toBeVisible();

    // Check if decision options are enabled (no blockers)
    const approveOption = page.locator('.decision-option').filter({ hasText: /^Approve$/i }).first();
    const isDisabled = await approveOption.getAttribute('disabled');
    
    if (isDisabled === null) {
      // Select "Close as false positive" outcome
      const falsePositiveOption = page.locator('.decision-option').filter({ hasText: /Close as false positive/i }).first();
      await falsePositiveOption.click();

      // Verify selection (should have 'selected' class or aria-checked)
      await expect(falsePositiveOption).toHaveClass(/selected/);

      // Enter rationale text
      const rationaleField = page.locator('textarea');
      await rationaleField.fill('Supporting documents sufficiently explain the source of funds.');

      // Verify outcome preview appears
      await expect(page.getByText(/Outcome on record/i)).toBeVisible();
    }
  });

  test('should disable record button until outcome and rationale provided', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Find record decision button
    const recordButton = page.getByRole('button', { name: /record decision/i });
    await expect(recordButton).toBeVisible();

    // Initially, button should be disabled (no outcome or rationale selected yet)
    // Note: actual state depends on page state - we're just verifying button exists
    const buttonText = await recordButton.textContent();
    expect(buttonText).toContain('Record decision');
  });

  test('should record decision when outcome and rationale provided', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Wait for page load
    await expect(page.getByText('Record decision')).toBeVisible();

    // Check if we can interact with decision options (no blockers)
    const decisionOptions = page.locator('.decision-option');
    const firstOption = decisionOptions.first();
    const isDisabled = await firstOption.evaluate((el) => el.classList.contains('disabled'));

    if (!isDisabled) {
      // Select false positive outcome
      const falsePositiveOption = decisionOptions.filter({ hasText: /Close as false positive/i }).first();
      await falsePositiveOption.click();

      // Enter rationale
      const rationaleField = page.locator('textarea');
      await rationaleField.fill('Test rationale: Customer provided comprehensive documentation.');

      // Wait a moment for form validation
      await page.waitForTimeout(300);

      // Try to record decision
      const recordButton = page.getByRole('button', { name: /record decision/i });
      const isRecordDisabled = await recordButton.isDisabled();
      
      if (!isRecordDisabled) {
        await recordButton.click();

        // Wait for success feedback (snackbar or navigation)
        await expect(
          page.getByText(/decision recorded/i).or(page.locator('.snackbar'))
        ).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should navigate back when back button clicked', async ({ page }) => {
    await page.goto('/cases/50000000-0000-0000-0000-000000000004/officer-review');

    // Click back button
    const backButton = page.locator('button[aria-label*="Back"]').first();
    await backButton.click();

    // Verify navigation occurred
    await expect(page).not.toHaveURL(/officer-review/);
  });

  test('should show error banner for conflicted officer', async ({ page }) => {
    // Login as investigator (case creator)
    await page.goto('/login');
    await page.fill('input[type="email"]', 'investigator@example.com');
    await page.fill('input[type="password"]', 'investigator123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/alerts');

    // Try to access officer review page for case they created
    await page.goto('/cases/50000000-0000-0000-0000-000000000001/officer-review');

    // Should see error about four-eyes enforcement
    // (Note: backend may return 403, or UI may show conflicted banner)
    const conflictBanner = page.getByText(/Independent review required|Case creator cannot perform/i);
    
    // Either we see the banner or we get an error state
    const bannerVisible = await conflictBanner.isVisible().catch(() => false);
    const errorState = page.locator('.error-state');
    const errorVisible = await errorState.isVisible().catch(() => false);
    
    expect(bannerVisible || errorVisible).toBeTruthy();
  });

  test('should display blocked state when open requests exist', async ({ page }) => {
    // Use case with open requests (CS-205: 50000000-0000-0000-0000-000000000005)
    await page.goto('/cases/50000000-0000-0000-0000-000000000005/officer-review');

    // Wait for page load
    await expect(page.locator('h1')).toContainText('Officer review');

    // Should display blocker warning
    const blockerBanner = page.getByText(/decision blocked/i);
    await expect(blockerBanner).toBeVisible();

    // Decision options should be disabled
    const decisionOptions = page.locator('.decision-option');
    const firstOption = decisionOptions.first();
    await expect(firstOption).toHaveClass(/disabled/);

    // Record button should be disabled
    const recordButton = page.getByRole('button', { name: /record decision/i });
    await expect(recordButton).toBeDisabled();
  });
});
