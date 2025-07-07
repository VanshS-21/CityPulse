import { FullConfig } from '@playwright/test'

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Cleaning up Playwright test environment...')
  
  // Clean up any global resources
  // This could include stopping test servers, cleaning up test data, etc.
  
  console.log('✅ Playwright test environment cleanup complete')
}

export default globalTeardown
