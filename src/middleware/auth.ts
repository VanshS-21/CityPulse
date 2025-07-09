/**
 * Authentication Middleware for CityPulse API Routes
 * Provides token validation and role-based authorization
 * Real Firebase Admin SDK implementation
 */

import { NextRequest, NextResponse } from 'next/server'
import { verifyFirebaseToken, getUserProfile } from '@/lib/firebase-admin'

export interface AuthenticatedUser {
  uid: string
  email: string | null
  name: string | null
  role: 'citizen' | 'admin' | 'moderator' | 'authority'
  emailVerified: boolean
}

export interface AuthRequest extends NextRequest {
  user?: AuthenticatedUser
}

/**
 * Verify Firebase ID token and extract user information
 */
export async function verifyToken(token: string): Promise<AuthenticatedUser | null> {
  try {
    // Verify the Firebase ID token and get user data
    const userData = await verifyFirebaseToken(token)

    if (!userData) {
      return null
    }

    // Get user profile for role information
    const userProfile = await getUserProfile(userData.uid)

    return {
      uid: userData.uid,
      email: userData.email,
      name: userData.name,
      role: userProfile?.role || userData.role as 'citizen' | 'admin' | 'moderator' | 'authority',
      emailVerified: userData.emailVerified,
    }
  } catch (error) {
    console.error('Token verification failed:', error)
    return null
  }
}

/**
 * Authentication middleware - requires valid token
 */
export async function requireAuth(request: NextRequest): Promise<{ user: AuthenticatedUser } | NextResponse> {
  const authHeader = request.headers.get('Authorization')
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return NextResponse.json(
      { error: 'Authentication required', success: false },
      { status: 401 }
    )
  }

  const token = authHeader.substring(7)
  const user = await verifyToken(token)

  if (!user) {
    return NextResponse.json(
      { error: 'Invalid or expired token', success: false },
      { status: 401 }
    )
  }

  return { user }
}

/**
 * Role-based authorization middleware
 */
export async function requireRole(
  request: NextRequest, 
  allowedRoles: Array<'citizen' | 'admin' | 'moderator' | 'authority'>
): Promise<{ user: AuthenticatedUser } | NextResponse> {
  const authResult = await requireAuth(request)
  
  if (authResult instanceof NextResponse) {
    return authResult // Return error response
  }

  const { user } = authResult

  if (!allowedRoles.includes(user.role)) {
    return NextResponse.json(
      { error: 'Insufficient permissions', success: false },
      { status: 403 }
    )
  }

  return { user }
}

/**
 * Admin-only middleware
 */
export async function requireAdmin(request: NextRequest): Promise<{ user: AuthenticatedUser } | NextResponse> {
  return requireRole(request, ['admin'])
}

/**
 * Authority or Admin middleware
 */
export async function requireAuthority(request: NextRequest): Promise<{ user: AuthenticatedUser } | NextResponse> {
  return requireRole(request, ['admin', 'authority'])
}

/**
 * Moderator, Authority, or Admin middleware
 */
export async function requireModerator(request: NextRequest): Promise<{ user: AuthenticatedUser } | NextResponse> {
  return requireRole(request, ['admin', 'authority', 'moderator'])
}

/**
 * Optional authentication - doesn't fail if no token provided
 */
export async function optionalAuth(request: NextRequest): Promise<{ user: AuthenticatedUser | null }> {
  const authHeader = request.headers.get('Authorization')
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return { user: null }
  }

  const token = authHeader.substring(7)
  const user = await verifyToken(token)

  return { user }
}

/**
 * Check if user owns resource (for user-specific operations)
 */
export function checkResourceOwnership(user: AuthenticatedUser, resourceUserId: string): boolean {
  // Admin can access any resource
  if (user.role === 'admin') {
    return true
  }
  
  // User can only access their own resources
  return user.uid === resourceUserId
}

/**
 * Rate limiting helper (basic implementation)
 */
const rateLimitMap = new Map<string, { count: number; resetTime: number }>()

export function checkRateLimit(identifier: string, maxRequests: number = 100, windowMs: number = 60000): boolean {
  const now = Date.now()
  const userLimit = rateLimitMap.get(identifier)

  if (!userLimit || now > userLimit.resetTime) {
    rateLimitMap.set(identifier, { count: 1, resetTime: now + windowMs })
    return true
  }

  if (userLimit.count >= maxRequests) {
    return false
  }

  userLimit.count++
  return true
}

/**
 * CORS headers for API responses
 */
export function getCorsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  }
}
