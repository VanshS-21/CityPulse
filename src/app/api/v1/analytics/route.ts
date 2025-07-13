import { NextRequest, NextResponse } from 'next/server'
import { withErrorHandler, forwardToBackend, getQueryParams, createBackendHeaders, createErrorResponse, createSuccessResponse, handleOptions } from '@/lib/api-utils'
import { optionalAuth, requireAuth, requireModerator, getCorsHeaders, AuthenticatedUser } from '@/middleware/auth'

/**
 * Analytics API Route Handler
 * Handles analytics with role-based access control
 */

const BACKEND_BASE_URL = process.env.BACKEND_API_URL || 'http://localhost:8000'

/**
 * GET /api/v1/analytics - Fetch analytics data (role-based access)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const endpoint = searchParams.get('endpoint') || 'kpis'

    // Define public and protected endpoints
    const publicEndpoints = ['public/summary', 'events/by-category']
    const protectedEndpoints = ['kpis', 'trends', 'events/by-location', 'performance', 'detailed']

    // Check if endpoint is valid
    if (!publicEndpoints.includes(endpoint) && !protectedEndpoints.includes(endpoint)) {
      return NextResponse.json(
        { error: 'Invalid analytics endpoint', success: false },
        { status: 400 }
      )
    }

    // Handle authentication based on endpoint type
    let user: AuthenticatedUser | null = null
    if (protectedEndpoints.includes(endpoint)) {
      // Require moderator role for protected analytics
      const authResult = await requireModerator(request)
      if (authResult instanceof NextResponse) {
        return authResult
      }
      user = authResult.user
    } else {
      // Optional auth for public endpoints
      const authResult = await optionalAuth(request)
      user = authResult.user
    }

    // Build query parameters
    const queryParams = new URLSearchParams()
    searchParams.forEach((value, key) => {
      if (key !== 'endpoint') {
        queryParams.append(key, value)
      }
    })

    const queryString = queryParams.toString()
    const url = `${BACKEND_BASE_URL}/v1/analytics/${endpoint}${queryString ? `?${queryString}` : ''}`

    // Prepare headers
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (user) {
      headers['X-User-ID'] = user.uid
      headers['X-User-Role'] = user.role
      headers['X-User-Email'] = user.email || ''
    }

    // Forward request to backend
    const response = await fetch(url, {
      method: 'GET',
      headers,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        { 
          error: errorData.detail || 'Failed to fetch analytics', 
          success: false 
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json({
      success: true,
      data: data
    }, { headers: getCorsHeaders() })

  } catch (error) {
    console.error('Analytics API error:', error)
    return NextResponse.json(
      { error: 'Internal server error', success: false },
      { status: 500 }
    )
  }
}

/**
 * POST /api/v1/analytics - Submit analytics event (requires authentication)
 */
export async function POST(request: NextRequest) {
  try {
    // Require authentication for submitting analytics events
    const authResult = await requireAuth(request)
    if (authResult instanceof NextResponse) {
      return authResult
    }

    const { user } = authResult
    const body = await request.json()

    // Validate required fields
    if (!body.event_type) {
      return NextResponse.json(
        { error: 'event_type is required', success: false },
        { status: 400 }
      )
    }

    // Add metadata with user context
    const analyticsData = {
      ...body,
      timestamp: new Date().toISOString(),
      source: 'web_frontend',
      user_agent: request.headers.get('User-Agent') || '',
      ip_address: request.headers.get('X-Forwarded-For') ||
                  request.headers.get('X-Real-IP') ||
                  'unknown',
      user_id: user.uid,
      user_role: user.role,
    }

    // Forward to backend analytics service
    const response = await fetch(`${BACKEND_BASE_URL}/v1/analytics/events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': user.uid,
        'X-User-Role': user.role,
        'X-User-Email': user.email || '',
      },
      body: JSON.stringify(analyticsData),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        { 
          error: errorData.detail || 'Failed to submit analytics event', 
          success: false 
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json({
      success: true,
      data: data
    }, { headers: getCorsHeaders() })

  } catch (error) {
    console.error('Analytics submission error:', error)
    return NextResponse.json(
      { error: 'Internal server error', success: false },
      { status: 500 }
    )
  }
}

/**
 * OPTIONS /api/v1/analytics - Handle preflight requests
 */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: getCorsHeaders(),
  })
}
