import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { API_ENDPOINTS } from '@/utils/constants'

// Mock handlers for API endpoints
export const handlers = [
  // Issues endpoint
  http.get('/v1/events', () => {
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

  // Users endpoint
  http.get('/v1/users', () => {
    return HttpResponse.json({
      data: [
        {
          id: '1',
          email: 'test@example.com',
          role: 'citizen',
          createdAt: '2023-12-07T00:00:00Z',
        },
      ],
    })
  }),

  // Analytics endpoint
  http.get('/v1/analytics', () => {
    return HttpResponse.json({
      data: {
        totalIssues: 100,
        resolvedIssues: 75,
        activeUsers: 50,
        avgResolutionTime: 72,
      },
    })
  }),

  // Auth endpoint
  http.post('/v1/auth/login', () => {
    return HttpResponse.json({
      data: {
        token: 'mock-jwt-token',
        user: {
          id: '1',
          email: 'test@example.com',
          role: 'citizen',
        },
      },
    })
  }),

  // Catch-all handler for unmatched requests
  http.get('*', ({ request }) => {
    console.warn(`Unhandled request: ${request.method} ${request.url}`)
    return HttpResponse.json({ error: 'Not found' }, { status: 404 })
  }),
]

// Setup MSW server
export const server = setupServer(...handlers)
