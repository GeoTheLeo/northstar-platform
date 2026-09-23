import { defineConfig } from "@playwright/test";

// The FastAPI model-serving service (services/copilot_api) must already be
// running separately on COPILOT_API_URL - it isn't started by this config.
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  reporter: "list",
  use: {
    baseURL: "http://localhost:3000",
  },
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: true,
    timeout: 30_000,
  },
});
