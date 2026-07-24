import { test, expect } from '@playwright/test';

test('has title and login form', async ({ page }) => {
  await page.goto('/admin/login');
  
  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Campus Copies/);

  // Expect the login form to be visible
  await expect(page.getByRole('heading', { name: /admin login/i })).toBeVisible();
  await expect(page.getByLabel(/email/i)).toBeVisible();
  await expect(page.getByLabel(/password/i)).toBeVisible();
  await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
});
