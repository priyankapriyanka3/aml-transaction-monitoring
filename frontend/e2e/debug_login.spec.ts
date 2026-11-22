// Debug login test
import { test, expect } from './_pipeline_guard';

test('debug login flow', async ({ page }) => {
  // Enable console logging
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.message));
  
  // Go to login page
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  
  console.log('Login page loaded');
  
  // Fill in credentials
  await page.fill('input[name="username"]', 'riya');
  await page.fill('input[name="password"]', 'password123');
  
  console.log('Credentials filled');
  
  // Listen for network requests
  page.on('response', response => {
    if (response.url().includes('/api/')) {
      console.log(`API RESPONSE: ${response.status()} ${response.url()}`);
    }
  });
  
  // Click login button
  await page.click('button[type="submit"]');
  
  console.log('Submit clicked, waiting for response...');
  
  // Wait a bit to see what happens
  await page.waitForTimeout(5000);
  
  // Check current URL
  const currentUrl = page.url();
  console.log('Current URL after login attempt:', currentUrl);
  
  // Check for any error messages
  const errorMessage = await page.locator('.bg-critical-container').textContent().catch(() => null);
  if (errorMessage) {
    console.log('Error message displayed:', errorMessage);
  }
  
  // Check if still on login page
  if (currentUrl.includes('/login')) {
    console.log('Still on login page - login failed');
    // Take a screenshot
    await page.screenshot({ path: 'login-failed.png', fullPage: true });
  } else {
    console.log('Navigated away from login - login succeeded');
  }
});
