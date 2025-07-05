import { test, expect } from '@playwright/test';

test.describe('Submit Report E2E', () => {
  test('should allow a user to submit a report', async ({ page }) => {
    // Navigate to the submit report page
    await page.goto('/submit-report');

    // Fill out the form
    await page.fill('input[name="title"]', 'Test Report from E2E Test');
    await page.fill('textarea[name="description"]', 'This is a test report submitted through an end-to-end test.');
    await page.fill('input[name="location"]', '123 Test St, Test City, TS 12345');

    // Submit the form
    await page.click('button[type="submit"]');

    // Wait for the success message
    const successMessage = await page.waitForSelector('text=/Report submitted successfully/i');
    expect(successMessage).not.toBeNull();
  });
});