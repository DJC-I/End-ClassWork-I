import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  testMatch: "phase46.spec.ts",
  fullyParallel: false,
  workers: 1,
  timeout: 40000,
  use: {
    baseURL: "http://127.0.0.1:8006",
    headless: true,
    viewport: { width: 1440, height: 1000 },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  reporter: [
    ["list"],
    ["json", { outputFile: "../docs/phase4_6/e2e-results.json" }],
  ],
  projects: [
    { name: "chromium", use: { browserName: "chromium", channel: "msedge" } },
  ],
});
