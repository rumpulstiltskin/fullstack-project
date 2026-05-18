import { expect, test } from "@playwright/test";

async function signIn(page: import("@playwright/test").Page) {
  await page.goto("/");
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
}

test.beforeEach(async ({ page }) => {
  await signIn(page);
});

test("loads the kanban board", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Playwright card")).toBeVisible();
});

test("added card persists after refresh", async ({ page }) => {
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Persistent card");
  await firstColumn.getByPlaceholder("Details").fill("Should survive refresh.");

  const putPromise = page.waitForResponse(
    (res) => res.url().includes("/api/board") && res.request().method() === "PUT"
  );
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Persistent card")).toBeVisible();
  await putPromise;

  await page.reload();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
  await expect(
    page.locator('[data-testid^="column-"]').first().getByText("Persistent card")
  ).toBeVisible();
});

test("moves a card between columns", async ({ page }) => {
  const backlogColumn = page.getByTestId("column-col-backlog");
  const reviewColumn = page.getByTestId("column-col-review");

  await backlogColumn.getByRole("button", { name: /add a card/i }).click();
  await backlogColumn.getByPlaceholder("Card title").fill("Card to drag");
  await backlogColumn.getByPlaceholder("Details").fill("Will be dragged.");
  await backlogColumn.getByRole("button", { name: /add card/i }).click();
  await expect(backlogColumn.getByText("Card to drag")).toBeVisible();

  const cardLocator = backlogColumn.locator('[data-testid^="card-"]').last();
  const cardBox = await cardLocator.boundingBox();
  const columnBox = await reviewColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();
  await expect(reviewColumn.getByText("Card to drag")).toBeVisible();
});

test("dragged card position persists after refresh", async ({ page }) => {
  const backlogColumn = page.getByTestId("column-col-backlog");
  const reviewColumn = page.getByTestId("column-col-review");

  const addPutPromise = page.waitForResponse(
    (res) => res.url().includes("/api/board") && res.request().method() === "PUT"
  );
  await backlogColumn.getByRole("button", { name: /add a card/i }).click();
  await backlogColumn.getByPlaceholder("Card title").fill("Drag persist card");
  await backlogColumn.getByPlaceholder("Details").fill("Drag test.");
  await backlogColumn.getByRole("button", { name: /add card/i }).click();
  await expect(backlogColumn.getByText("Drag persist card")).toBeVisible();
  await addPutPromise;

  const cardLocator = backlogColumn.locator('[data-testid^="card-"]').last();
  const cardBox = await cardLocator.boundingBox();
  const columnBox = await reviewColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  const dragPutPromise = page.waitForResponse(
    (res) => res.url().includes("/api/board") && res.request().method() === "PUT"
  );
  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();
  await expect(reviewColumn.getByText("Drag persist card")).toBeVisible();
  await dragPutPromise;

  await page.reload();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
  await expect(
    page.getByTestId("column-col-review").getByText("Drag persist card")
  ).toBeVisible();
});
