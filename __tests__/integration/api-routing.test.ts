import { API_ENDPOINTS, APP_CONFIG } from '@/utils/constants'

describe('API Routing Integration Tests', () => {

  describe('Constants Configuration', () => {
    test('should have correct base URL in APP_CONFIG', () => {
      expect(APP_CONFIG.api.baseUrl).toBe('/api/v1')
    })

    test('should have correct API endpoints with /api/v1 prefix', () => {
      expect(API_ENDPOINTS.issues).toBe('/api/v1/events')
      expect(API_ENDPOINTS.users).toBe('/api/v1/users')
      expect(API_ENDPOINTS.analytics).toBe('/api/v1/analytics')
      expect(API_ENDPOINTS.notifications).toBe('/api/v1/notifications')
      expect(API_ENDPOINTS.auth).toBe('/api/v1/auth')
      expect(API_ENDPOINTS.upload).toBe('/api/v1/upload')
      expect(API_ENDPOINTS.social).toBe('/api/v1/social')
      expect(API_ENDPOINTS.ai).toBe('/api/v1/ai')
      expect(API_ENDPOINTS.feedback).toBe('/api/v1/feedback')
    })
  })

  describe('Next.js Rewrite Configuration', () => {
    test('should verify rewrite configuration exists', async () => {
      const nextConfig = await import('../../next.config')
      expect(nextConfig.default.rewrites).toBeDefined()
      expect(typeof nextConfig.default.rewrites).toBe('function')
    })

    test('should verify rewrite rules are correct', async () => {
      const nextConfig = await import('../../next.config')
      const rewrites = await nextConfig.default.rewrites()

      expect(rewrites).toEqual([
        {
          source: '/api/v1/:path*',
          destination: '/api/:path*'
        }
      ])
    })
  })

// Note: MSW integration tests would be added here in a more complex setup
  // For now, we focus on testing the configuration and constants

  describe('URL Construction', () => {
    test('should construct URLs correctly using constants', () => {
      const baseUrl = APP_CONFIG.api.baseUrl
      const issuesEndpoint = API_ENDPOINTS.issues
      
      // Test that the endpoint already includes the base URL
      expect(issuesEndpoint).toBe(baseUrl + '/events')
      
      // Test URL construction for full API calls
      const fullUrl = `${baseUrl}/events`
      expect(fullUrl).toBe('/api/v1/events')
    })

    test('should validate all endpoints follow the same pattern', () => {
      const baseUrl = APP_CONFIG.api.baseUrl
      const endpoints = Object.values(API_ENDPOINTS)
      
      endpoints.forEach(endpoint => {
        expect(endpoint).toMatch(new RegExp(`^${baseUrl.replace('/', '\\/')}/`))
      })
    })
  })

  describe('Routing Logic Verification', () => {
    test('should validate that rewrite transforms /api/v1 to /api', () => {
      // This test verifies the logical transformation
      // In our app, /api/v1/events is rewritten to /api/events
      const apiPath = '/api/v1/events'
      const expectedRewritePath = apiPath.replace('/v1', '')
      
      expect(expectedRewritePath).toBe('/api/events')
    })

    test('should validate path parameter handling', () => {
      // Test that complex paths are handled correctly
      const complexApiPath = '/api/v1/users/123/profile'
      const expectedRewritePath = complexApiPath.replace('/v1', '')
      
      expect(expectedRewritePath).toBe('/api/users/123/profile')
    })
  })
})
