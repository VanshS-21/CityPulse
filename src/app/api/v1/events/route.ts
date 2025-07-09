import { NextRequest, NextResponse } from 'next/server'
import { apiGateway } from '@/lib/api-gateway'
import { validateData } from '@/lib/validation'
import { createIssueFormSchema } from '@/lib/validation'

/**
 * Events API Route Handler
 * Proxies requests to the backend events service
 */

const BACKEND_BASE_URL = process.env.BACKEND_API_URL || 'http://localhost:8000'

/**
 * GET /api/v1/events - Fetch events
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const params = Object.fromEntries(searchParams.entries())

    // Forward request to backend
    const response = await fetch(`${BACKEND_BASE_URL}/v1/events`, {
      method: 'GET',
      headers: {
        'Authorization': request.headers.get('Authorization') || '',
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch events', success: false },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error('Events API error:', error)
    return NextResponse.json(
      { error: 'Internal server error', success: false },
      { status: 500 }
    )
  }
}

/**
 * POST /api/v1/events - Create new event
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validate request body
    const validation = validateData(createIssueFormSchema, body)
    if (!validation.success) {
      return NextResponse.json(
        { 
          error: 'Validation failed', 
          success: false,
          details: validation.errors.errors 
        },
        { status: 400 }
      )
    }

    // Transform frontend data to backend format
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
      metadata: {
        source: 'web_frontend',
        user_agent: request.headers.get('User-Agent') || '',
      }
    }

    // Forward request to backend
    const response = await fetch(`${BACKEND_BASE_URL}/v1/events`, {
      method: 'POST',
      headers: {
        'Authorization': request.headers.get('Authorization') || '',
        'Content-Type': 'application/json',
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
 * OPTIONS /api/v1/events - Handle preflight requests
 */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
