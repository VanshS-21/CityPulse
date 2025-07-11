/**
 * MSW Example - API Mocking Integration Test
 * 
 * This file demonstrates how to use MSW for API mocking in integration tests.
 * This is a working example that shows how to set up MSW v2 for testing API routing.
 */

import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { API_ENDPOINTS } from '@/utils/constants'

// Mock API handlers
const handlers = [
  // Mock successful API response
  http.get('*/v1/events', () => {
    return HttpResponse.json({
      data: [
        {
          id: '1',
          title: 'Test Issue',
          description: 'Test description',
          category: 'infrastructure',
          priority: 'high',
          status: 'open',
          location: { lat: 40.7128, lng: -74.0060 },
          createdAt: '2023-12-07T00:00:00Z',
        },
      ],
      meta: {
        total: 1,
        page: 1,
        limit: 20,
      },
    })
  }),

  // Mock error response
  http.get('*/v1/error', () => {
    return HttpResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    )
  }),

  // Mock with dynamic response based on parameters
  http.get('*/v1/users/:id', ({ params }) => {
    const { id } = params
    return HttpResponse.json({
      data: {
        id: id,
        email: `user${id}@example.com`,
        role: 'citizen',
        createdAt: '2023-12-07T00:00:00Z',
      },
    })
  }),

  // Mock POST request
  http.post('*/v1/auth/login', async ({ request }) => {
    const credentials = await request.json()
    
    // You can add validation logic here
    if (credentials.email === 'test@example.com') {
      return HttpResponse.json({
        data: {
          token: 'mock-jwt-token',
          user: {
            id: '1',
            email: credentials.email,
            role: 'citizen',
          },
        },
      })
    }
    
    return HttpResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    )
  }),
]

// Setup MSW server
const server = setupServer(...handlers)

describe('MSW Example Tests', () => {
  // Start server before tests
  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'bypass' })
  })

  // Reset handlers after each test
  afterEach(() => {
    server.resetHandlers()
  })

  // Close server after tests
  afterAll(() => {
    server.close()
  })

  describe('API Mocking Examples', () => {
    test('should mock successful API response', async () => {
      const response = await fetch('http://localhost/v1/events')
      const data = await response.json()
      
      expect(response.status).toBe(200)
      expect(data.data).toHaveLength(1)
      expect(data.data[0].title).toBe('Test Issue')
    })

    test('should mock error response', async () => {
      const response = await fetch('http://localhost/v1/error')
      const data = await response.json()
      
      expect(response.status).toBe(500)
      expect(data.error).toBe('Internal Server Error')
    })

    test('should mock dynamic response with parameters', async () => {
      const response = await fetch('http://localhost/v1/users/123')
      const data = await response.json()
      
      expect(response.status).toBe(200)
      expect(data.data.id).toBe('123')
      expect(data.data.email).toBe('user123@example.com')
    })

    test('should mock POST request with body validation', async () => {
      const response = await fetch('http://localhost/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123',
        }),
      })
      
      const data = await response.json()
      
      expect(response.status).toBe(200)
      expect(data.data.token).toBe('mock-jwt-token')
      expect(data.data.user.email).toBe('test@example.com')
    })

    test('should mock failed authentication', async () => {
      const response = await fetch('http://localhost/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'invalid@example.com',
          password: 'wrongpassword',
        }),
      })
      
      const data = await response.json()
      
      expect(response.status).toBe(401)
      expect(data.error).toBe('Invalid credentials')
    })
  })

  describe('Runtime Handler Override', () => {
    test('should override handler at runtime', async () => {
      // Override the handler for this specific test
      server.use(
        http.get('*/v1/events', () => {
          return HttpResponse.json({
            data: [],
            meta: { total: 0, page: 1, limit: 20 },
          })
        })
      )

      const response = await fetch('http://localhost/v1/events')
      const data = await response.json()
      
      expect(response.status).toBe(200)
      expect(data.data).toHaveLength(0)
      expect(data.meta.total).toBe(0)
    })
  })

  describe('Next.js Rewrite Simulation', () => {
    test('should simulate Next.js rewrite behavior', async () => {
      // In a real Next.js app, /api/v1/events would be rewritten to /v1/events
      // This test simulates that behavior by testing the destination path
      const apiPath = API_ENDPOINTS.issues // '/api/v1/events'
      const rewrittenPath = apiPath.replace('/api', '') // '/v1/events'
      
      // Test that our mock handler responds to the rewritten path
      const response = await fetch(`http://localhost${rewrittenPath}`)
      const data = await response.json()
      
      expect(response.status).toBe(200)
      expect(data.data).toHaveLength(1)
      expect(data.data[0].title).toBe('Test Issue')
    })
  })
})

/**
 * Usage Notes:
 * 
 * 1. MSW v2 uses `http.get()` instead of `rest.get()`
 * 2. Use `HttpResponse.json()` instead of `res(ctx.json())`
 * 3. The server setup should be done in beforeAll/afterAll hooks
 * 4. Use `server.resetHandlers()` to clean up between tests
 * 5. Use `server.use()` to override handlers at runtime
 * 6. Mock endpoints should match the destination paths (e.g., /v1/events)
 * 7. The '*' prefix in paths allows matching any domain
 * 
 * For more complex scenarios, you can:
 * - Add authentication checks
 * - Validate request bodies
 * - Test error conditions
 * - Mock WebSocket connections
 * - Test file uploads
 * - Simulate network delays
 */
