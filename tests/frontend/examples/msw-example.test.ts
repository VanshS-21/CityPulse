/**
 * Advanced API Mocking Test - MSW Concepts Implementation
 *
 * This demonstrates the CONCEPTS that MSW tests (request interception,
 * URL pattern matching, body processing, etc.) using a more reliable approach.
 *
 * NOTE: This shows the difference between simple mocking and MSW-style testing:
 * - Simple mocking: Just mock the function call
 * - MSW-style: Actually process requests, extract parameters, validate bodies
 */

import { API_ENDPOINTS } from '@/utils/constants'

// Advanced mock that simulates MSW's request processing capabilities
class MockRequestProcessor {
  private handlers: Map<
    string,
    (req: MockRequest) => MockResponse | Promise<MockResponse>
  > = new Map()

  // Simulate MSW's http.get() registration
  get(
    pattern: string,
    handler: (req: MockRequest) => MockResponse | Promise<MockResponse>
  ) {
    this.handlers.set(`GET:${pattern}`, handler)
  }

  // Simulate MSW's http.post() registration
  post(
    pattern: string,
    handler: (req: MockRequest) => MockResponse | Promise<MockResponse>
  ) {
    this.handlers.set(`POST:${pattern}`, handler)
  }

  // Process request like MSW does - extract params, parse body, etc.
  async processRequest(
    method: string,
    url: string,
    options?: RequestInit
  ): Promise<MockResponse> {
    const urlObj = new URL(url)

    // Find matching handler (simplified pattern matching)
    for (const [key, handler] of this.handlers) {
      const [handlerMethod, ...patternParts] = key.split(':')
      const pattern = patternParts.join(':') // Rejoin in case pattern contains ':'

      if (
        handlerMethod === method &&
        this.matchesPattern(urlObj.pathname, pattern)
      ) {
        const mockRequest: MockRequest = {
          method,
          url,
          params: this.extractParams(urlObj.pathname, pattern),
          json: async () =>
            options?.body ? JSON.parse(options.body as string) : {},
          headers: new Headers(options?.headers),
        }
        return await handler(mockRequest)
      }
    }

    const availableHandlers = Array.from(this.handlers.keys())
    throw new Error(
      `No handler found for ${method} ${urlObj.pathname}. Available: ${availableHandlers.join(', ')}`
    )
  }

  public matchesPattern(path: string, pattern: string): boolean {
    // Simple pattern matching (MSW does this more sophisticatedly)
    // Convert pattern like "*/v1/users/:id" to regex
    let regex = pattern
      .replace(/\*/g, '.*') // * becomes .*
      .replace(/:(\w+)/g, '([^/]+)') // :id becomes ([^/]+)

    // For patterns starting with *, we need to handle the case where path doesn't start with /
    if (pattern.startsWith('*')) {
      regex = regex.replace(/^\.\*/, '.*')
    }

    const regexPattern = new RegExp(`^${regex}$`)
    return regexPattern.test(path)
  }

  public extractParams(path: string, pattern: string): Record<string, string> {
    // Extract URL parameters like MSW does
    const params: Record<string, string> = {}

    // Handle wildcard patterns like */v1/users/:id
    if (pattern.includes('*')) {
      // For patterns like */v1/users/:id, we need to find where v1 starts in the path
      const patternWithoutWildcard = pattern.replace(/^\*/, '')
      const pathParts = path.split('/')
      const patternParts = patternWithoutWildcard.split('/')

      // Find where the pattern starts matching in the path
      let startIndex = -1
      for (let i = 0; i <= pathParts.length - patternParts.length; i++) {
        let matches = true
        for (let j = 0; j < patternParts.length; j++) {
          const patternPart = patternParts[j]
          const pathPart = pathParts[i + j]

          if (!patternPart.startsWith(':') && patternPart !== pathPart) {
            matches = false
            break
          }
        }
        if (matches) {
          startIndex = i
          break
        }
      }

      if (startIndex >= 0) {
        patternParts.forEach((part, index) => {
          if (part.startsWith(':')) {
            const paramName = part.slice(1)
            const pathIndex = startIndex + index
            if (pathIndex < pathParts.length) {
              params[paramName] = pathParts[pathIndex]
            }
          }
        })
      }
    }

    return params
  }
}

interface MockRequest {
  method: string
  url: string
  params: Record<string, string>
  json: () => Promise<any>
  headers: Headers
}

interface MockResponse {
  status: number
  data: any
}

// Create mock processor that simulates MSW behavior
let mockProcessor = new MockRequestProcessor()

// Setup handlers that simulate MSW's sophisticated request processing
mockProcessor.get('*/v1/events', () => ({
  status: 200,
  data: {
    data: [
      {
        id: '1',
        title: 'Test Issue',
        description: 'Test description',
        category: 'infrastructure',
        priority: 'high',
        status: 'open',
        location: { lat: 40.7128, lng: -74.006 },
        createdAt: '2023-12-07T00:00:00Z',
      },
    ],
    meta: {
      total: 1,
      page: 1,
      limit: 10,
    },
  },
}))

mockProcessor.get('*/v1/error', () => ({
  status: 500,
  data: { error: 'Internal Server Error' },
}))

// This demonstrates MSW's parameter extraction capability
mockProcessor.get('*/v1/users/:id', req => ({
  status: 200,
  data: {
    data: {
      id: req.params.id, // Actually extracted from URL!
      name: `User ${req.params.id}`,
      email: `user${req.params.id}@example.com`,
    },
  },
}))

// This demonstrates MSW's request body processing
mockProcessor.post('*/v1/auth/login', async req => {
  const body = await req.json() // Actually parses request body!

  // Real credential validation like MSW would do
  if (body.email === 'test@example.com' && body.password === 'password123') {
    return {
      status: 200,
      data: {
        data: {
          token: 'mock-jwt-token',
          user: {
            id: '1',
            email: body.email,
            name: 'Test User',
          },
        },
      },
    }
  }

  return {
    status: 401,
    data: { error: 'Invalid credentials' },
  }
})

// Mock fetch to use our advanced processor
const originalFetch = global.fetch
global.fetch = jest
  .fn()
  .mockImplementation(async (url: string, options?: RequestInit) => {
    try {
      const method = options?.method || 'GET'
      const mockResponse = await mockProcessor.processRequest(
        method,
        url,
        options
      )

      return {
        ok: mockResponse.status >= 200 && mockResponse.status < 300,
        status: mockResponse.status,
        json: () => Promise.resolve(mockResponse.data),
        text: () => Promise.resolve(JSON.stringify(mockResponse.data)),
      } as Response
    } catch (error) {
      // Fallback to original fetch if no handler matches
      return originalFetch(url, options)
    }
  })

describe('Advanced API Mocking - MSW Concepts Implementation', () => {
  beforeEach(() => {
    // Reset handlers before each test to avoid interference
    mockProcessor = new MockRequestProcessor()

    // Re-setup default handlers
    mockProcessor.get('*/v1/events', () => ({
      status: 200,
      data: {
        data: [
          {
            id: '1',
            title: 'Test Issue',
            description: 'Test description',
            category: 'infrastructure',
            priority: 'high',
            status: 'open',
            location: { lat: 40.7128, lng: -74.006 },
            createdAt: '2023-12-07T00:00:00Z',
          },
        ],
        meta: {
          total: 1,
          page: 1,
          limit: 10,
        },
      },
    }))

    mockProcessor.get('*/v1/error', () => ({
      status: 500,
      data: { error: 'Internal Server Error' },
    }))

    mockProcessor.get('*/v1/users/:id', req => ({
      status: 200,
      data: {
        data: {
          id: req.params.id,
          name: `User ${req.params.id}`,
          email: `user${req.params.id}@example.com`,
        },
      },
    }))

    mockProcessor.post('*/v1/auth/login', async req => {
      const body = await req.json()

      if (
        body.email === 'test@example.com' &&
        body.password === 'password123'
      ) {
        return {
          status: 200,
          data: {
            data: {
              token: 'mock-jwt-token',
              user: {
                id: '1',
                email: body.email,
                name: 'Test User',
              },
            },
          },
        }
      }

      return {
        status: 401,
        data: { error: 'Invalid credentials' },
      }
    })

    // Update the global mock to use the current processor
    global.fetch = jest
      .fn()
      .mockImplementation(async (url: string, options?: RequestInit) => {
        try {
          const method = options?.method || 'GET'
          // Use the current mockProcessor instance
          const mockResponse = await mockProcessor.processRequest(
            method,
            url,
            options
          )

          return {
            ok: mockResponse.status >= 200 && mockResponse.status < 300,
            status: mockResponse.status,
            json: () => Promise.resolve(mockResponse.data),
            text: () => Promise.resolve(JSON.stringify(mockResponse.data)),
          } as Response
        } catch (error) {
          // Return a mock error response instead of calling original fetch
          const urlObj = new URL(url)
          const errorMessage = error instanceof Error ? error.message : 'Unknown error'
          return {
            ok: false,
            status: 404,
            json: () =>
              Promise.resolve({
                error: `No handler found for ${options?.method || 'GET'} ${urlObj.pathname}. Error: ${errorMessage}`,
              }),
            text: () =>
              Promise.resolve(
                JSON.stringify({
                  error: `No handler found for ${options?.method || 'GET'} ${urlObj.pathname}. Error: ${errorMessage}`,
                })
              ),
          } as Response
        }
      })
  })

  afterAll(() => {
    // Restore original fetch
    global.fetch = originalFetch
  })

  describe('MSW-Style Request Processing (What MSW Actually Tests)', () => {
    test('should process URL patterns and return structured responses', async () => {
      // This demonstrates what MSW does: pattern matching and structured responses
      const response = await fetch('http://localhost/v1/events')
      const data = await response.json()

      // Our processor matched the pattern and returned structured data
      expect(response.status).toBe(200)
      expect(data.data).toHaveLength(1)
      expect(data.data[0].title).toBe('Test Issue')
      expect(data.meta.total).toBe(1)
    })

    test('should handle error responses with proper status codes', async () => {
      // Tests error handling like MSW does
      const response = await fetch('http://localhost/v1/error')
      const data = await response.json()

      expect(response.status).toBe(500)
      expect(data.error).toBe('Internal Server Error')
    })

    test('should extract URL parameters like MSW does', async () => {
      // Test parameter extraction directly first
      const testParams = mockProcessor.extractParams(
        '/v1/users/123',
        '*/v1/users/:id'
      )
      expect(testParams.id).toBe('123')

      // Test pattern matching
      const urlObj = new URL('http://localhost/v1/users/123')
      const matches = mockProcessor.matchesPattern(
        urlObj.pathname,
        '*/v1/users/:id'
      )
      expect(matches).toBe(true)

      // This is what MSW actually does - extracts parameters from URLs
      const response = await fetch('http://localhost/v1/users/123')
      const data = await response.json()

      // Our processor actually extracted "123" from the URL pattern ":id"
      expect(response.status).toBe(200)
      expect(data.data.id).toBe('123') // This came from URL parameter extraction!
      expect(data.data.name).toBe('User 123')
      expect(data.data.email).toBe('user123@example.com')
    })

    test('should parse POST request bodies and validate like MSW does', async () => {
      // This demonstrates MSW's request body processing capability
      const response = await fetch('http://localhost/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123',
        }),
      })
      const data = await response.json()

      // Our processor actually parsed the JSON body and validated credentials
      expect(response.status).toBe(200)
      expect(data.data.token).toBe('mock-jwt-token')
      expect(data.data.user.email).toBe('test@example.com')
    })

    test('should handle authentication validation like MSW does', async () => {
      // Tests request body validation and conditional responses
      const response = await fetch('http://localhost/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'invalid@example.com',
          password: 'wrongpassword',
        }),
      })
      const data = await response.json()

      // Our processor validated the credentials and returned appropriate error
      expect(response.status).toBe(401)
      expect(data.error).toBe('Invalid credentials')
    })
  })

  describe('Dynamic Handler Override (MSW Concept)', () => {
    test('should demonstrate runtime handler replacement like MSW', async () => {
      // First request uses default handler
      let response = await fetch('http://localhost/v1/events')
      let data = await response.json()

      expect(data.data).toHaveLength(1)
      expect(data.meta.total).toBe(1)

      // Override the handler at runtime (simulating MSW's server.use())
      mockProcessor.get('*/v1/events', () => ({
        status: 200,
        data: {
          data: [],
          meta: { total: 0 },
        },
      }))

      // Second request uses the overridden handler
      response = await fetch('http://localhost/v1/events')
      data = await response.json()

      expect(data.data).toHaveLength(0)
      expect(data.meta.total).toBe(0)
    })
  })

  describe('API Configuration and URL Processing', () => {
    test('should demonstrate URL rewriting concepts like Next.js', async () => {
      // Test the actual API endpoint configuration
      const apiPath = API_ENDPOINTS.issues // '/api/v1/events'
      const rewrittenPath = apiPath.replace('/api', '') // '/v1/events'

      expect(apiPath).toBe('/api/v1/events')
      expect(rewrittenPath).toBe('/v1/events')

      // Our processor handles the rewritten path
      const response = await fetch(`http://localhost${rewrittenPath}`)
      const data = await response.json()

      // Pattern matching worked and returned structured response
      expect(response.status).toBe(200)
      expect(data.data).toHaveLength(1)
      expect(data.meta.total).toBe(1)
    })

    test('should validate API endpoints configuration', () => {
      // Test that our API endpoints are correctly configured
      expect(API_ENDPOINTS.issues).toBe('/api/v1/events')
      expect(API_ENDPOINTS.users).toBe('/api/v1/users')
      expect(API_ENDPOINTS.auth).toBe('/api/v1/auth')
      expect(API_ENDPOINTS.analytics).toBe('/api/v1/analytics')
      expect(API_ENDPOINTS.notifications).toBe('/api/v1/notifications')
    })
  })
})
