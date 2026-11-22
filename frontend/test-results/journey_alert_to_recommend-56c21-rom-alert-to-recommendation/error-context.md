# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: journey_alert_to_recommendation.spec.ts >> Journey: Alert Triage → Case Creation → Investigation → Recommendation >> should complete full investigator workflow from alert to recommendation
- Location: e2e/journey_alert_to_recommendation.spec.ts:17:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=/Case CS-\\d+/')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" locator('text=/Case CS-\\d+/') with timeout 5000ms
  - waiting for locator('text=/Case CS-\\d+/')

```

```yaml
- banner:
  - button "Navigate up to Alerts":
    - img
  - heading "CS-003 · Riya Sharma" [level=1]
  - paragraph: Case workspace
  - status: INVESTIGATING
  - button "More case actions":
    - img
- tablist "Case sections":
  - tab "Overview" [selected]
  - tab "Linked alerts (1)"
  - tab "Requests (0)"
  - tab "Activity"
- main:
  - region "Case summary":
    - heading "Case summary" [level=2]
    - text: CRITICAL
    - term: Case ID
    - definition: CS-003
    - term: Owner
    - definition: Riya Sharma
    - term: Opened
    - definition: Nov 22, 2026, 05:40 AM
    - term: Status
    - definition: INVESTIGATING
    - term: Linked alerts
    - definition: "1"
    - term: Flagged value
    - definition: $285,000.00
  - region "Investigation notes":
    - heading "Investigation notes" [level=2]
    - group "Note stage":
      - button "Triage"
      - button "Investigation" [pressed]
      - button "Info request"
      - button "Findings"
    - text: Note · INVESTIGATION
    - textbox "Note · INVESTIGATION":
      - /placeholder: Add investigation note...
    - paragraph: Edits create a new visible version.
    - paragraph: 0 / 2000
    - button "Save note" [disabled]
    - img
    - heading "No notes yet" [level=3]
    - paragraph: Add the first investigation note for this stage.
  - article "Evidence gap · Source of funds":
    - heading "Evidence gap · Source of funds" [level=2]
    - paragraph: Documentation is missing for TX-8821 (USD 48,500).
    - button "Request information"
  - region "Investigator recommendation":
    - heading "Investigator recommendation" [level=2]
    - text: Not a final decision
    - paragraph: Your recommendation goes to an independent officer, who decides separately.
    - radiogroup "Recommendation outcome":
      - radio "Recommend closure — activity explained"
      - radio "Recommend further review"
      - radio "Recommend escalation for enhanced scrutiny"
    - text: Findings summary *
    - textbox "Findings summary *":
      - /placeholder: Summarize key findings (minimum 50 characters)
    - paragraph: 0 / 2000
    - button "Submit recommendation for review" [disabled]
    - paragraph: Opens the review handoff (wireframe 5).
- button "Request information"
- button "Save note"
- navigation "Primary":
  - link "Alerts":
    - /url: /alerts
    - img
    - text: Alerts
  - link "Cases":
    - /url: /cases/CS-003
    - img
    - text: Cases
```

# Test source

```ts
  1   | import { test, expect } from './_pipeline_guard';
  2   | 
  3   | /**
  4   |  * E2E Journey Test: Alert Triage → Case Creation → Investigation → Recommendation Submission
  5   |  * 
  6   |  * This test simulates a complete investigator workflow:
  7   |  * 1. Login as investigator (riya)
  8   |  * 2. Navigate to alert queue
  9   |  * 3. Assign an alert and triage it with "INVESTIGATE" outcome
  10  |  * 4. Create a case from the alert
  11  |  * 5. Navigate to the case workspace
  12  |  * 6. Add investigation notes
  13  |  * 7. Submit a recommendation
  14  |  * 8. Verify the case status transitions to REVIEW_READY
  15  |  */
  16  | test.describe('Journey: Alert Triage → Case Creation → Investigation → Recommendation', () => {
  17  |   test('should complete full investigator workflow from alert to recommendation', async ({ page }) => {
  18  |     // ===== Step 1: Login =====
  19  |     await page.goto('/login');
  20  |     await page.fill('input[name="username"]', 'riya');
  21  |     await page.fill('input[name="password"]', 'password123');
  22  |     await page.click('button[type="submit"]');
  23  |     await page.waitForURL('/alerts', { timeout: 10000 });
  24  |     await page.waitForLoadState('networkidle');
  25  | 
  26  |     console.log('✓ Step 1: Logged in as investigator');
  27  | 
  28  |     // ===== Step 2: Navigate to Alert Queue and Verify Load =====
  29  |     await expect(page.locator('h1', { hasText: 'Alerts' })).toBeVisible();
  30  |     await page.waitForSelector('[aria-label="Loading alert queue"], article', { timeout: 10000 });
  31  |     await page.waitForSelector('article', { timeout: 10000 });
  32  | 
  33  |     console.log('✓ Step 2: Alert queue loaded');
  34  | 
  35  |     // ===== Step 3: Assign an Alert =====
  36  |     // Find first alert with "Assign to me" button
  37  |     const firstAlert = page.locator('article').first();
  38  |     await expect(firstAlert).toBeVisible({ timeout: 10000 });
  39  | 
  40  |     // Look for an unassigned alert
  41  |     const assignButton = page.locator('article').locator('button', { hasText: 'Assign to me' }).first();
  42  |     await expect(assignButton).toBeVisible({ timeout: 10000 });
  43  |     await assignButton.click();
  44  | 
  45  |     await page.waitForTimeout(2000); // Wait for assignment to complete and reload
  46  |     console.log('✓ Step 3: Alert assigned');
  47  | 
  48  |     // ===== Step 4: Triage Alert with "INVESTIGATE" Outcome =====
  49  |     // After reload, find the first alert with a "Triage" button (the one we just assigned)
  50  |     await page.waitForLoadState('networkidle');
  51  |     const assignedAlertWithTriage = page.locator('article', { has: page.locator('button', { hasText: 'Triage' }) }).first();
  52  |     const triageButton = assignedAlertWithTriage.locator('button', { hasText: 'Triage' });
  53  |     await expect(triageButton).toBeVisible();
  54  |     await triageButton.click();
  55  | 
  56  |     // Wait for triage modal
  57  |     await expect(page.locator('[role="dialog"]')).toBeVisible({ timeout: 5000 });
  58  |     await expect(page.locator('text=/Triage alert/')).toBeVisible();
  59  | 
  60  |     // Select "INVESTIGATE" outcome (first radio button)
  61  |     const investigateOption = page.locator('[role="radio"]').first();
  62  |     await expect(investigateOption).toBeVisible();
  63  |     await investigateOption.click();
  64  | 
  65  |     // Fill rationale
  66  |     const rationaleField = page.locator('textarea#rationale');
  67  |     await expect(rationaleField).toBeVisible();
  68  |     await rationaleField.fill('High-risk cross-border transaction requires detailed investigation. Multiple rules triggered indicating suspicious pattern.');
  69  | 
  70  |     // Save disposition
  71  |     const saveButton = page.locator('button', { hasText: 'Save disposition' });
  72  |     await expect(saveButton).toBeVisible();
  73  |     await saveButton.click();
  74  | 
  75  |     // Wait for modal to close and page to reload
  76  |     await page.waitForTimeout(3000);
  77  |     await page.waitForLoadState('networkidle');
  78  |     console.log('✓ Step 4: Alert triaged with INVESTIGATE outcome');
  79  | 
  80  |     // ===== Step 5: Create Case from Alert =====
  81  |     // After triage and reload, find the first alert with "Create case" button
  82  |     const triagedAlertWithCreateCase = page.locator('article', { has: page.locator('button', { hasText: 'Create case' }) }).first();
  83  |     const createCaseButton = triagedAlertWithCreateCase.locator('button', { hasText: 'Create case' });
  84  |     await expect(createCaseButton).toBeVisible({ timeout: 5000 });
  85  |     await expect(createCaseButton).toBeEnabled();
  86  |     await createCaseButton.click();
  87  | 
  88  |     // Wait for navigation to case workspace
  89  |     await page.waitForURL(/\/cases\/CS-\d+/, { timeout: 10000 });
  90  |     await page.waitForLoadState('networkidle');
  91  | 
  92  |     console.log('✓ Step 5: Case created and navigated to case workspace');
  93  | 
  94  |     // ===== Step 6: Verify Case Overview Loaded =====
> 95  |     await expect(page.locator('text=/Case CS-\\d+/')).toBeVisible({ timeout: 5000 });
      |                                                       ^ Error: expect(locator).toBeVisible() failed
  96  |     await expect(page.locator('text=/Status.*INVESTIGATING/i')).toBeVisible();
  97  | 
  98  |     console.log('✓ Step 6: Case overview loaded with INVESTIGATING status');
  99  | 
  100 |     // ===== Step 7: Add Investigation Notes =====
  101 |     // Find note textarea
  102 |     const noteTextarea = page.locator('textarea').first();
  103 |     await expect(noteTextarea).toBeVisible({ timeout: 5000 });
  104 |     
  105 |     await noteTextarea.fill('Initial investigation commenced. Reviewed transaction history and customer risk profile. Multiple high-value cross-border transfers identified. Further analysis required on counterparty relationships.');
  106 | 
  107 |     // Save note
  108 |     const saveNoteButton = page.locator('button', { hasText: /Save note|Submit note/i });
  109 |     await expect(saveNoteButton).toBeVisible();
  110 |     await saveNoteButton.click();
  111 | 
  112 |     await page.waitForTimeout(2000);
  113 |     console.log('✓ Step 7: Investigation note added');
  114 | 
  115 |     // Verify note appears in the case
  116 |     await expect(page.locator('text=/Initial investigation commenced/')).toBeVisible({ timeout: 5000 });
  117 | 
  118 |     // ===== Step 8: Submit Recommendation =====
  119 |     // Scroll to or find the recommendation section
  120 |     const recommendationSection = page.locator('text=/Submit.*recommendation|Recommendation/i').first();
  121 |     await expect(recommendationSection).toBeVisible({ timeout: 5000 });
  122 | 
  123 |     // Select recommendation outcome
  124 |     const substantiateOption = page.locator('[role="radio"]', { hasText: /Substantiate|File.*SAR|Escalate/i }).first();
  125 |     await expect(substantiateOption).toBeVisible({ timeout: 5000 });
  126 |     await substantiateOption.click();
  127 | 
  128 |     // Fill findings summary
  129 |     const findingsSummary = page.locator('textarea#findings-summary, textarea[name="findings-summary"], textarea').last();
  130 |     await expect(findingsSummary).toBeVisible();
  131 |     await findingsSummary.fill('Based on investigation, transaction pattern indicates potential money laundering activity. Customer engaged in multiple high-value cross-border transfers with sanctioned jurisdiction connections. Recommend filing SAR and escalating to compliance officer for review.');
  132 | 
  133 |     // Submit recommendation
  134 |     const submitRecommendationButton = page.locator('button', { hasText: /Submit.*recommendation/i });
  135 |     await expect(submitRecommendationButton).toBeVisible();
  136 |     await expect(submitRecommendationButton).toBeEnabled();
  137 |     await submitRecommendationButton.click();
  138 | 
  139 |     await page.waitForTimeout(3000);
  140 |     console.log('✓ Step 8: Recommendation submitted');
  141 | 
  142 |     // ===== Step 9: Verify Case Status Transitions to REVIEW_READY =====
  143 |     // After recommendation submission, the case should transition to REVIEW_READY
  144 |     await page.reload();
  145 |     await page.waitForLoadState('networkidle');
  146 | 
  147 |     // Check for REVIEW_READY or SUBMITTED status
  148 |     await expect(page.locator('text=/Status.*REVIEW.*READY|Status.*SUBMITTED/i')).toBeVisible({ timeout: 5000 });
  149 | 
  150 |     console.log('✓ Step 9: Case status transitioned to REVIEW_READY');
  151 | 
  152 |     // ===== Verify Final State =====
  153 |     // Verify recommendation outcome is displayed
  154 |     await expect(page.locator('text=/Substantiate|File.*SAR|Escalate/i')).toBeVisible();
  155 |     
  156 |     // Verify findings summary is displayed
  157 |     await expect(page.locator('text=/Based on investigation/')).toBeVisible();
  158 | 
  159 |     console.log('✅ Journey completed successfully: Alert → Triage → Case → Investigation → Recommendation');
  160 |   });
  161 | });
  162 | 
```