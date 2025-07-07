// Global teardown for Jest tests

module.exports = async () => {
  console.log('🧹 Cleaning up test environment...')
  
  // Clean up any global resources
  // This could include closing database connections, stopping test servers, etc.
  
  console.log('✅ Test environment cleanup complete')
}
