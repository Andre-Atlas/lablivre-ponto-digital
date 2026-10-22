import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright config for web_admin E2E.
 * Requires the full stack running (frontend + backend) and a seeded LO catalog.
 */
export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
