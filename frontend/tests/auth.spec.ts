import { expect, test } from "@playwright/test";

test("shows login form when not authenticated", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(0);
});

test("shows error on wrong credentials", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("wrongpassword");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByText("Invalid credentials")).toBeVisible();
});

test("login and logout flow", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();

  await page.getByRole("button", { name: /sign out/i }).click();
  await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
});
