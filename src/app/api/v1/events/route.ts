import { NextRequest, NextResponse } from 'next/server'
import { forwardToBackend, createErrorResponse, createSuccessResponse, withErrorHandler, getQueryParams, createBackendHeaders, handleOptions } from '@/lib/api-utils'
import { optionalAuth, requireAuth, requireAuthority, getCorsHeaders } from '@/middleware/auth'
import { validateData, createIssueFormSchema } from '@/lib/validation'

/**
 * Events API Route Handler
 * Handles events with real authentication and authorization
 */

const BACKEND_BASE_URL = process.env.BACKEND_API_URL || 'http://localhost:8000'

/**
 * GET /api/v1/events - Fetch events (public endpoint with optional auth)
 */
export async function GET(request: NextRequest) {
  try {
    // Optional authentication - public can view events but authenticated users get more data
    const { user } = await optionalAuth(request)

    const { searchParams } = new URL(request.url)
    const params = Object.fromEntries(searchParams.entries())

    // Add user context to request if authenticated
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (user) {
      // Create a simple token for backend (in production, use proper JWT)
      headers['X-User-ID'] = user.uid
      headers['X-User-Role'] = user.role
    }

    // Forward request to backend
    const response = await fetch(`${BACKEND_BASE_URL}/v1/events?${new URLSearchParams(params)}`, {
      method: 'GET',
      headers,
    })

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch events', success: false },
        { status: response.status }
      )
    }

    const data = await response.json()

    // Add CORS headers
    const responseHeaders = getCorsHeaders()

    return NextResponse.json(data, { headers: responseHeaders })

  } catch (error) {
    console.error('Events API error:', error)
    return NextResponse.json(
      { error: 'Internal server error', success: false },
      { status: 500 }
    )
  }
}

/**
 * POST /api/v1/events - Create new event (requires authentication)
 */
export async function POST(request: NextRequest) {
  try {
    // Require authentication for creating events
    const authResult = await requireAuth(request)
    if (authResult instanceof NextResponse) {
      return authResult // Return error response
    }

    const { user } = authResult
    const body = await request.json()

    // Validate request body
    const validation = validateData(createIssueFormSchema, body)
    if (!validation.success) {
      return NextResponse.json(
        {
          error: 'Validation failed',
          success: false,
          message: 'Please check your input data'
        },
        { status: 400 }
      )
    }

    // Transform frontend data to backend format with user context
    const backendData = {
      title: validation.data.title,
      description: validation.data.description,
      category: validation.data.category,
      severity: validation.data.priority, // Map priority to severity
      location: {
        latitude: validation.data.location.latitude,
        longitude: validation.data.location.longitude,
        address: validation.data.location.address,
        city: validation.data.location.city,
        state: validation.data.location.state,
        postal_code: validation.data.location.zipCode,
      },
      tags: validation.data.tags,
      reporter_id: user.uid, // Add authenticated user as reporter
      reporter_email: user.email,
      metadata: {
        source: 'web_frontend',
        user_agent: request.headers.get('User-Agent') || '',
        reporter_role: user.role,
      }
    }

    // Forward request to backend with user context
    const response = await fetch(`${BACKEND_BASE_URL}/v1/events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': user.uid,
        'X-User-Role': user.role,
        'X-User-Email': user.email || '',
      },
      body: JSON.stringify(backendData),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        { 
          error: errorData.detail || 'Failed to create event', 
          success: false 
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    // Transform backend response to frontend format
    const frontendData = {
      success: true,
      data: {
        id: data.id,
        title: data.title,
        description: data.description,
        category: data.category,
        priority: data.severity, // Map severity back to priority
        status: data.status,
        location: {
          latitude: data.location.latitude,
          longitude: data.location.longitude,
          address: data.location.address,
          city: data.location.city,
          state: data.location.state,
          zipCode: data.location.postal_code,
        },
        images: data.images || [],
        reportedBy: data.user_id,
        createdAt: new Date(data.created_at),
        updatedAt: new Date(data.updated_at),
        tags: data.tags || [],
        upvotes: 0,
        downvotes: 0,
      }
    }

    return NextResponse.json(frontendData, { status: 201 })

  } catch (error) {
    console.error('Events creation error:', error)
    return NextResponse.json(
      { error: 'Internal server error', success: false },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/v1/events - Update event (requires authority role or ownership)
 */
export async function PUT(request: NextRequest) {
  try {
    // Require authentication
    const authResult = await requireAuth(request)
    if (authResult instanceof NextResponse) {
      return authResult
    }

    const { user } = authResult
    const body = await request.json()
    const { eventId, ...updateData } = body

    if (!eventId) {
      return NextResponse.json(
        { error: 'Event ID is required', success: false },
        { status: 400 }
      )
    }

    // Forward request to backend
    const response = await fetch(`${BACKEND_BASE_URL}/v1/events/${eventId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': user.uid,
        'X-User-Role': user.role,
        'X-User-Email': user.email || '',
      },
      body: JSON.stringify(updateData),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        {
          error: errorData.detail || 'Failed to update event',
          success: false
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json({ success: true, data }, { headers: getCorsHeaders() })

  } catch (error) {
    console.error('Event update error:', error)
    return NextResponse.json(
      { error: 'Internal server error', success: false },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/v1/events - Delete event (requires authority role)
 */
export async function DELETE(request: NextRequest) {
  try {
    // Require authority role for deletion
    const authResult = await requireAuthority(request)
    if (authResult instanceof NextResponse) {
      return authResult
    }

    const { user } = authResult
    const { searchParams } = new URL(request.url)
    const eventId = searchParams.get('id')

    if (!eventId) {
      return NextResponse.json(
        { error: 'Event ID is required', success: false },
        { status: 400 }
      )
    }

    // Forward request to backend
    const response = await fetch(`${BACKEND_BASE_URL}/v1/events/${eventId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': user.uid,
        'X-User-Role': user.role,
        'X-User-Email': user.email || '',
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        {
          error: errorData.detail || 'Failed to delete event',
          success: false
        },
        { status: response.status }
      )
    }

    return NextResponse.json(
      { success: true, message: 'Event deleted successfully' },
      { headers: getCorsHeaders() }
    )

  } catch (error) {
    console.error('Event deletion error:', error)
    return NextResponse.json(
      { error: 'Internal server error', success: false },
      { status: 500 }
    )
  }
}

/**
 * OPTIONS /api/v1/events - Handle preflight requests
 */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: getCorsHeaders(),
  })
}
