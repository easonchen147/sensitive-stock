import { defineConfig, devices } from "@playwright/test";

const frontendPort = Number(process.env.FRONTEND_SMOKE_PORT || 3311);
const baseURL = process.env.PLAYWRIGHT_BASE_URL || `http://127.0.0.1:${frontendPort}`;

export default defineConfig({
  testDir: "./tests/smoke",
  timeout: 45_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  reporter: [["list"]],
  use: {
    baseURL,
    trace: "retain-on-failure",
  },
  webServer: {
    command: "node scripts/smoke-server.mjs",
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      BACKEND_SMOKE_PORT: String(process.env.BACKEND_SMOKE_PORT || 5311),
      FRONTEND_SMOKE_PORT: String(frontendPort),
    },
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
