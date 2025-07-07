// Global setup for Jest tests
const { execSync } = require('child_process')
const path = require('path')

module.exports = async () => {
  console.log('🚀 Setting up CityPulse test environment...')
  
  // Set test environment variables
  process.env.NODE_ENV = 'test'
  process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000'
  process.env.NEXT_PUBLIC_APP_URL = 'http://localhost:3000'
  process.env.DATABASE_URL = 'postgresql://test:test@localhost:5432/citypulse_test'
  
  // Create test reports directory
  const fs = require('fs')
  const reportsDir = path.join(process.cwd(), 'test-reports')
  if (!fs.existsSync(reportsDir)) {
    fs.mkdirSync(reportsDir, { recursive: true })
  }
  
  console.log('✅ Test environment setup complete')
}
