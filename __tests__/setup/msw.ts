import { setupServer } from 'msw/node'
import { rest } from 'msw'
import { API_ENDPOINTS } from '@/utils/constants'

// Mock handlers for API endpoints
export const handlers = [
  // Issues endpoint
  rest.get('/v1/events', (req, res, ctx) => {
    return res(
      ctx.json({
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
    )
  }),

  // Users endpoint
  rest.get('/v1/users', (req, res, ctx) => {
    return res(
      ctx.json({
        data: [
          {
            id: '1',
            email: 'test@example.com',
            role: 'citizen',
            createdAt: '2023-12-07T00:00:00Z',
          },
        ],
      })
    )
  }),

  // Analytics endpoint
  rest.get('/v1/analytics', (req, res, ctx) => {
    return res(
      ctx.json({
        data: {
          totalIssues: 100,
          resolvedIssues: 75,
          activeUsers: 50,
          avgResolutionTime: 72,
        },
      })
    )
  }),

  // Auth endpoint
  rest.post('/v1/auth/login', (req, res, ctx) => {
    return res(
      ctx.json({
        data: {
          token: 'mock-jwt-token',
          user: {
            id: '1',
            email: 'test@example.com',
            role: 'citizen',
          },
        },
      })
    )
  }),

  // Catch-all handler for unmatched requests
  rest.get('*', (req, res, ctx) => {
    console.warn(`Unhandled request: ${req.method} ${req.url}`)
    return res(ctx.status(404), ctx.json({ error: 'Not found' }))
  }),
]

// Setup MSW server
export const server = setupServer(...handlers)
