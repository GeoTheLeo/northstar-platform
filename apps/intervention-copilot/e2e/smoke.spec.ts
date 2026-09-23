import { expect, test } from "@playwright/test";

test("dashboard shows the KPI cards", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "NorthStar Intervention Copilot" })).toBeVisible();
  await expect(page.getByText("Students at risk")).toBeVisible();
  await expect(page.getByText("Pending approvals")).toBeVisible();
  await expect(page.getByText("Executed this week")).toBeVisible();
});

test("copilot console renders and the example prompt fills the input", async ({ page }) => {
  await page.goto("/copilot");

  const textarea = page.locator("textarea");
  await expect(textarea).toBeVisible();
  await expect(page.getByRole("button", { name: "Send" })).toBeVisible();

  await page.getByText("Use example prompt").click();
  await expect(textarea).not.toHaveValue("");
});

test("approval queue renders with a pending section or an empty state", async ({ page }) => {
  await page.goto("/queue");

  await expect(page.getByRole("heading", { name: "Approval queue" })).toBeVisible();
  await expect(page.getByText(/^Pending \(\d+\)$/)).toBeVisible();

  const hasEmptyState = await page
    .getByText("No interventions are waiting on review.")
    .isVisible()
    .catch(() => false);
  const hasApproveButton = await page
    .getByRole("button", { name: "Approve" })
    .first()
    .isVisible()
    .catch(() => false);

  expect(hasEmptyState || hasApproveButton).toBe(true);
});
