import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './src/app/submit-report/__tests__',
  testMatch: 'e2e.test.tsx',
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:3000'
      },
    },
  ],
});
