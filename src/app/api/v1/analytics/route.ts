import { NextRequest, NextResponse } from 'next/server'

/**
 * Analytics API Route Handler
 * Proxies requests to the backend analytics service
 */

const BACKEND_BASE_URL = process.env.BACKEND_API_URL || 'http://localhost:8000'

/**
 * GET /api/v1/analytics - Fetch analytics data
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const endpoint = searchParams.get('endpoint') || 'kpis'
    
    // Validate endpoint to prevent path traversal
    const allowedEndpoints = ['kpis', 'trends', 'public/summary', 'events/by-category', 'events/by-location', 'performance']
    if (!allowedEndpoints.includes(endpoint)) {
      return NextResponse.json(
        { error: 'Invalid analytics endpoint', success: false },
        { status: 400 }
      )
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

    // Forward request to backend
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': request.headers.get('Authorization') || '',
        'Content-Type': 'application/json',
        'X-API-Key': request.headers.get('X-API-Key') || '',
      },
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
    })

  } catch (error) {
    console.error('Analytics API error:', error)
    return NextResponse.json(
      { error: 'Internal server error', success: false },
      { status: 500 }
    )
  }
}

/**
 * POST /api/v1/analytics - Submit analytics event
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validate required fields
    if (!body.event_type) {
      return NextResponse.json(
        { error: 'event_type is required', success: false },
        { status: 400 }
      )
    }

    // Add metadata
    const analyticsData = {
      ...body,
      timestamp: new Date().toISOString(),
      source: 'web_frontend',
      user_agent: request.headers.get('User-Agent') || '',
      ip_address: request.headers.get('X-Forwarded-For') || 
                  request.headers.get('X-Real-IP') || 
                  'unknown',
    }

    // Forward to backend analytics service
    const response = await fetch(`${BACKEND_BASE_URL}/v1/analytics/events`, {
      method: 'POST',
      headers: {
        'Authorization': request.headers.get('Authorization') || '',
        'Content-Type': 'application/json',
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
    })

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
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
    },
  })
}
