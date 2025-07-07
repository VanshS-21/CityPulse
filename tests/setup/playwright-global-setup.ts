import { chromium, FullConfig } from '@playwright/test'

async function globalSetup(config: FullConfig) {
  console.log('🚀 Setting up Playwright test environment...')
  
  // Set up test environment variables
  process.env.NODE_ENV = 'test'
  process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000'
  process.env.NEXT_PUBLIC_APP_URL = 'http://localhost:3000'
  
  // Create test reports directory
  const fs = require('fs')
  const path = require('path')
  const reportsDir = path.join(process.cwd(), 'test-reports')
  if (!fs.existsSync(reportsDir)) {
    fs.mkdirSync(reportsDir, { recursive: true })
  }
  
  // Warm up the browser
  const browser = await chromium.launch()
  await browser.close()
  
  console.log('✅ Playwright test environment setup complete')
}

export default globalSetup
