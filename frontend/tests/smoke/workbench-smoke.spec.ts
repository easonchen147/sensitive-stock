import { expect, test, type Page } from "@playwright/test";

const adminPassword = process.env.SMOKE_ADMIN_PASSWORD || "SensitiveStock-Internal-MVP";

async function login(page: Page) {
  await page.goto("/login");
  await page.locator("#username").fill("admin");
  await page.locator("#password").fill(adminPassword);
  await page.locator(".auth-submit").click();
  await expect(page).toHaveURL(/\/$/);
  await expect(page.locator(".dashboard-grid")).toBeVisible();
}

test("login page renders without an authenticated session", async ({ page }) => {
  await page.goto("/login");

  await expect(page.locator(".auth-card")).toBeVisible();
  await expect(page.locator(".hero-title")).toContainText("敏感股票研究台");
  await expect(page.locator("#username")).toHaveValue("admin");
  await expect(page.locator("#password")).toBeVisible();
});

test("protected pages redirect unauthenticated users to login", async ({ page }) => {
  await page.goto("/market");

  await expect(page).toHaveURL(/\/login\?next=%2Fmarket$/);
  await expect(page.locator(".auth-card")).toBeVisible();
});

const protectedWorkbenchPages = [
  ["/backtests", "量化回测台", "提交前快速复核"],
  ["/market", "行情与快讯工作台", "复盘历史"],
  ["/screener", "条件选股工作台", "运行一次选股后查看候选标的。"],
  ["/diagnosis", "结构化诊股工作台", "生成报告后查看结构化段落。"],
  ["/factors", "因子分析工作台", "运行因子分析后查看排名。"],
  ["/portfolio", "组合优化工作台", "运行组合优化后查看目标权重。"],
] as const;

test("authenticated user can enter dashboard and all research workbenches", async ({ page }) => {
  await login(page);

  for (const [route, title, representativeEntry] of protectedWorkbenchPages) {
    await page.goto(route);
    await expect(page.locator(".workbench-hero")).toBeVisible();
    await expect(page.locator(".hero-title")).toContainText(title);
    await expect(page.getByText(representativeEntry)).toBeVisible();
  }

  await page.goto("/market");
  await expect(page.getByText("行情与快讯工作台")).toBeVisible();
  await expect(page.getByText("预测历史与评估")).toBeVisible();
});

test("dashboard remains available in a mobile viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page);

  await expect(page.locator(".shell-nav")).toBeVisible();
  await expect(page.locator(".dashboard-grid")).toBeVisible();
  await expect(page.locator(".hero-title")).toBeVisible();
  await expect(page.getByText("A 股研究工作台")).toBeVisible();
});
