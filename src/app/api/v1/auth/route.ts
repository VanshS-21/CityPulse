import { NextRequest, NextResponse } from 'next/server'
import { validateData } from '@/lib/validation'
import { loginSchema, registerSchema } from '@/lib/validation'
import {
  verifyFirebaseToken,
  createCustomToken,
  createOrUpdateUserProfile,
  getUserProfile,
  revokeRefreshTokens,
  createFirebaseUser,
  getAdminAuth,
} from '@/lib/firebase-admin'

/**
 * Authentication API Route Handler
 * Handles Firebase Auth integration with real Firebase Admin SDK
 */

const BACKEND_BASE_URL = process.env.BACKEND_API_URL || 'http://localhost:8000'

/**
 * POST /api/v1/auth - Handle authentication requests
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, ...authData } = body

    switch (action) {
      case 'login':
        return handleLogin(authData, request)
      case 'register':
        return handleRegister(authData, request)
      case 'logout':
        return handleLogout(request)
      case 'refresh':
        return handleTokenRefresh(request)
      case 'verify-token':
        return handleTokenVerification(request)
      default:
        return NextResponse.json(
          { error: 'Invalid action', success: false },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error('Auth API error:', error)
    return NextResponse.json(
      { error: 'Internal server error', success: false },
      { status: 500 }
    )
  }
}

/**
 * Handle user login - Real Firebase Auth implementation
 */
async function handleLogin(authData: any, request: NextRequest) {
  try {
    // For login, we expect the client to send us the Firebase ID token
    // The client-side Firebase Auth handles the actual authentication
    const { idToken } = authData

    if (!idToken) {
      return NextResponse.json(
        { error: 'ID token is required for login', success: false },
        { status: 400 }
      )
    }

    // Verify the Firebase ID token and get user data
    const userData = await verifyFirebaseToken(idToken)

    if (!userData) {
      return NextResponse.json(
        { error: 'Invalid or expired token', success: false },
        { status: 401 }
      )
    }

    // Create custom token with role claims
    const customToken = await createCustomToken(userData.uid, {
      role: userData.role,
      email: userData.email,
      name: userData.name
    })

    const response = {
      success: true,
      data: {
        user: {
          id: userData.uid,
          email: userData.email,
          name: userData.name,
          role: userData.role as 'citizen' | 'admin' | 'moderator' | 'authority',
          emailVerified: userData.emailVerified,
          createdAt: new Date(),
          lastLoginAt: new Date(),
        },
        token: customToken,
        expiresIn: 3600, // 1 hour
      }
    }

    return NextResponse.json(response)
  } catch (error: any) {
    console.error('Login error:', error)

    // Handle specific Firebase Auth errors
    if (error?.code === 'auth/id-token-expired') {
      return NextResponse.json(
        { error: 'Token expired', success: false },
        { status: 401 }
      )
    } else if (error?.code === 'auth/id-token-revoked') {
      return NextResponse.json(
        { error: 'Token revoked', success: false },
        { status: 401 }
      )
    } else if (error?.code === 'auth/user-not-found') {
      return NextResponse.json(
        { error: 'User not found', success: false },
        { status: 404 }
      )
    }

    return NextResponse.json(
      { error: 'Login failed', success: false },
      { status: 401 }
    )
  }
}

/**
 * Handle user registration - Real Firebase Auth implementation
 */
async function handleRegister(authData: any, request: NextRequest) {
  // Validate registration data
  const validation = validateData(registerSchema, authData)
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

  try {
    const { email, password, name } = validation.data

    // Create user in Firebase Auth
    const { uid, userRecord } = await createFirebaseUser({
      email: email,
      password: password,
      displayName: name,
      emailVerified: false,
    })

    // Create user profile in Firestore with default role
    const userProfile = await createOrUpdateUserProfile(uid, {
      email: email,
      name: name,
      role: 'citizen',
      emailVerified: false,
    })

    // Create custom token with role claims
    const customToken = await createCustomToken(uid, {
      role: 'citizen',
      email: email,
      name: name
    })

    // Send email verification (optional - can be done client-side)
    try {
      const auth = getAdminAuth()
      await auth.generateEmailVerificationLink(email)
    } catch (emailError) {
      console.warn('Could not send email verification:', emailError)
    }

    const response = {
      success: true,
      data: {
        user: {
          id: uid,
          email: email,
          name: name,
          role: 'citizen' as const,
          emailVerified: false,
          createdAt: new Date(userRecord.metadata.creationTime),
          lastLoginAt: new Date(userRecord.metadata.creationTime),
        },
        token: customToken,
        expiresIn: 3600, // 1 hour
      }
    }

    return NextResponse.json(response, { status: 201 })
  } catch (error: any) {
    console.error('Registration error:', error)

    // Handle specific Firebase Auth errors
    if (error?.code === 'auth/email-already-exists') {
      return NextResponse.json(
        { error: 'Email already exists', success: false },
        { status: 409 }
      )
    } else if (error?.code === 'auth/invalid-email') {
      return NextResponse.json(
        { error: 'Invalid email address', success: false },
        { status: 400 }
      )
    } else if (error?.code === 'auth/weak-password') {
      return NextResponse.json(
        { error: 'Password is too weak', success: false },
        { status: 400 }
      )
    }

    return NextResponse.json(
      { error: 'Registration failed', success: false },
      { status: 400 }
    )
  }
}

/**
 * Handle user logout - Real Firebase Auth implementation
 */
async function handleLogout(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')

    if (authHeader && authHeader.startsWith('Bearer ')) {
      const idToken = authHeader.substring(7)

      try {
        // Verify the token and get the user
        const userData = await verifyFirebaseToken(idToken)

        if (userData) {
          // Revoke all refresh tokens for the user
          await revokeRefreshTokens(userData.uid)
          console.log(`Revoked refresh tokens for user: ${userData.uid}`)
        }
      } catch (tokenError) {
        console.warn('Could not revoke tokens during logout:', tokenError)
        // Continue with logout even if token revocation fails
      }
    }

    return NextResponse.json({
      success: true,
      message: 'Logged out successfully'
    })
  } catch (error) {
    console.error('Logout error:', error)
    return NextResponse.json(
      { error: 'Logout failed', success: false },
      { status: 500 }
    )
  }
}

/**
 * Handle token refresh - Real Firebase Auth implementation
 */
async function handleTokenRefresh(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Invalid refresh token', success: false },
        { status: 401 }
      )
    }

    const idToken = authHeader.substring(7)

    // Verify the current token
    const userData = await verifyFirebaseToken(idToken)

    if (!userData) {
      return NextResponse.json(
        { error: 'Invalid or expired token', success: false },
        { status: 401 }
      )
    }

    // Get fresh user data
    const userProfile = await getUserProfile(userData.uid)

    // Create new custom token with updated claims
    const customToken = await createCustomToken(userData.uid, {
      role: userProfile?.role || userData.role,
      email: userData.email,
      name: userData.name
    })

    const response = {
      success: true,
      data: {
        token: customToken,
        expiresIn: 3600, // 1 hour
        user: {
          id: userData.uid,
          email: userData.email,
          name: userData.name,
          role: userProfile?.role || userData.role,
          emailVerified: userData.emailVerified,
        }
      }
    }

    return NextResponse.json(response)
  } catch (error: any) {
    console.error('Token refresh error:', error)

    if (error?.code === 'auth/id-token-expired' || error?.code === 'auth/id-token-revoked') {
      return NextResponse.json(
        { error: 'Token expired or revoked', success: false },
        { status: 401 }
      )
    }

    return NextResponse.json(
      { error: 'Token refresh failed', success: false },
      { status: 401 }
    )
  }
}

/**
 * Handle token verification
 */
async function handleTokenVerification(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'No token provided', success: false },
        { status: 401 }
      )
    }

    const idToken = authHeader.substring(7)

    // Verify the token
    const userData = await verifyFirebaseToken(idToken)

    if (!userData) {
      return NextResponse.json(
        {
          success: true,
          data: { valid: false },
          error: 'Invalid or expired token'
        },
        { status: 200 }
      )
    }

    // Get user profile
    const userProfile = await getUserProfile(userData.uid)

    const response = {
      success: true,
      data: {
        valid: true,
        user: {
          id: userData.uid,
          email: userData.email,
          name: userData.name,
          role: userProfile?.role || userData.role,
          emailVerified: userData.emailVerified,
        }
      }
    }

    return NextResponse.json(response)
  } catch (error) {
    console.error('Token verification error:', error)
    return NextResponse.json(
      {
        success: true,
        data: { valid: false },
        error: 'Invalid token'
      },
      { status: 200 } // Return 200 but with valid: false
    )
  }
}

/**
 * GET /api/v1/auth - Get current user info
 */
export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Unauthorized', success: false },
        { status: 401 }
      )
    }

    const idToken = authHeader.substring(7)

    // Verify the token and get user info
    const userData = await verifyFirebaseToken(idToken)

    if (!userData) {
      return NextResponse.json(
        { error: 'Invalid or expired token', success: false },
        { status: 401 }
      )
    }

    const userProfile = await getUserProfile(userData.uid)

    const response = {
      success: true,
      data: {
        user: {
          id: userData.uid,
          email: userData.email,
          name: userData.name,
          role: userProfile?.role || userData.role,
          emailVerified: userData.emailVerified,
          createdAt: userProfile?.createdAt || new Date(),
          lastLoginAt: new Date(),
        }
      }
    }

    return NextResponse.json(response)
  } catch (error) {
    console.error('Get user error:', error)
    return NextResponse.json(
      { error: 'Failed to get user info', success: false },
      { status: 500 }
    )
  }
}

/**
 * Helper function to get CORS headers
 */
function getCorsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  }
}

/**
 * OPTIONS /api/v1/auth - Handle preflight requests
 */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
