# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: wireframe_02_case_workspace.spec.ts >> Wireframe 02: Case Workspace >> should display case activity timeline
- Location: e2e/wireframe_02_case_workspace.spec.ts:137:3

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('h1')
Expected substring: "CS-"
Received string:    "Login"
Timeout: 10000ms

Call log:
  - Expect "toContainText" locator('h1') with timeout 10000ms
  - waiting for locator('h1')
    24 × locator resolved to <h1 class="text-3xl font-bold mb-2 text-on-surface">Login</h1>
       - unexpected value "Login"

```

```yaml
- heading "Login" [level=1]
```

# Test source

```ts
  43  | 
  44  |     // Wait for navigation to case page
  45  |     await page.waitForURL(/\/cases\/.+/, { timeout: 10000 });
  46  | 
  47  |     // Verify case workspace loaded
  48  |     await expect(page.locator('h1')).toContainText('CS-');
  49  |     await expect(page.locator('text=/Case workspace/i')).toBeVisible();
  50  |   });
  51  | 
  52  |   test('should display case overview with metadata', async ({ page }) => {
  53  |     // Navigate to a known case from seed (CS-001)
  54  |     await page.goto('/cases/CS-001');
  55  |     await page.waitForLoadState('networkidle');
  56  | 
  57  |     // Verify case header
  58  |     await expect(page.locator('h1')).toContainText('CS-');
  59  |     
  60  |     // Verify case summary section
  61  |     await expect(page.locator('text=/Case summary/i')).toBeVisible();
  62  |     
  63  |     // Verify status badge
  64  |     await expect(page.locator('text=/Investigating|Under review|Pending/i').first()).toBeVisible();
  65  |     
  66  |     // Verify linked alerts section
  67  |     await expect(page.locator('text=/Linked alert/i')).toBeVisible();
  68  |   });
  69  | 
  70  |   test('should save investigation note', async ({ page }) => {
  71  |     // Navigate to a known case
  72  |     await page.goto('/cases/CS-001');
  73  |     await page.waitForLoadState('networkidle');
  74  | 
  75  |     // Wait for page to load
  76  |     await expect(page.locator('h1')).toContainText('CS-', { timeout: 10000 });
  77  | 
  78  |     // Find investigation notes section
  79  |     await expect(page.locator('text=/Investigation notes/i')).toBeVisible();
  80  | 
  81  |     // Find note textarea
  82  |     const noteTextarea = page.locator('textarea').first();
  83  |     await expect(noteTextarea).toBeVisible();
  84  | 
  85  |     // Clear and enter new note
  86  |     await noteTextarea.clear();
  87  |     await noteTextarea.fill('Test investigation note added via E2E test with sufficient detail for validation.');
  88  | 
  89  |     // Click save note button
  90  |     const saveNoteBtn = page.locator('button', { hasText: /Save note/i }).first();
  91  |     await expect(saveNoteBtn).toBeVisible();
  92  |     await saveNoteBtn.click();
  93  | 
  94  |     // Wait for save to complete
  95  |     await page.waitForTimeout(2000);
  96  | 
  97  |     // Verify success (note should appear in list or success message)
  98  |     await expect(page.locator('text=/Test investigation note|Note saved|saved successfully/i')).toBeVisible({ timeout: 5000 });
  99  |   });
  100 | 
  101 |   test('should submit recommendation', async ({ page }) => {
  102 |     // Navigate to a known case
  103 |     await page.goto('/cases/CS-001');
  104 |     await page.waitForLoadState('networkidle');
  105 | 
  106 |     // Wait for page to load
  107 |     await expect(page.locator('h1')).toContainText('CS-', { timeout: 10000 });
  108 | 
  109 |     // Scroll to recommendation section
  110 |     const recommendationSection = page.locator('text=/Investigator recommendation|Recommendation/i').first();
  111 |     await expect(recommendationSection).toBeVisible({ timeout: 10000 });
  112 |     await recommendationSection.scrollIntoViewIfNeeded();
  113 | 
  114 |     // Select a recommendation outcome (first radio button)
  115 |     const firstRadio = page.locator('[role="radio"]').first();
  116 |     await expect(firstRadio).toBeVisible();
  117 |     await firstRadio.click();
  118 | 
  119 |     // Fill findings summary
  120 |     const findingsTextarea = page.locator('textarea#findings, textarea[aria-label*="findings" i], textarea[placeholder*="findings" i]').first();
  121 |     await expect(findingsTextarea).toBeVisible({ timeout: 5000 });
  122 |     await findingsTextarea.clear();
  123 |     await findingsTextarea.fill('Detailed findings summary explaining the investigation outcome with sufficient detail to meet the minimum character requirement for submission validation.');
  124 | 
  125 |     // Submit recommendation
  126 |     const submitBtn = page.locator('button', { hasText: /Submit recommendation/i }).first();
  127 |     await expect(submitBtn).toBeVisible();
  128 |     await submitBtn.click();
  129 | 
  130 |     // Wait for submission
  131 |     await page.waitForTimeout(2000);
  132 | 
  133 |     // Verify success (either navigation or message)
  134 |     await expect(page.locator('text=/submitted|success|review/i')).toBeVisible({ timeout: 5000 });
  135 |   });
  136 | 
  137 |   test('should display case activity timeline', async ({ page }) => {
  138 |     // Navigate to a known case
  139 |     await page.goto('/cases/CS-001');
  140 |     await page.waitForLoadState('networkidle');
  141 | 
  142 |     // Wait for page to load
> 143 |     await expect(page.locator('h1')).toContainText('CS-', { timeout: 10000 });
      |                                      ^ Error: expect(locator).toContainText(expected) failed
  144 | 
  145 |     // Look for activity section
  146 |     const activitySection = page.locator('text=/Recent activity|Activity/i');
  147 |     await expect(activitySection).toBeVisible({ timeout: 5000 });
  148 |     
  149 |     // Verify activity timeline has entries
  150 |     await expect(page.locator('text=/Case created|Note saved|created from/i')).toBeVisible();
  151 |   });
  152 | });
  153 | 
```