/**
 * Input Validation Middleware
 * Provides comprehensive input validation and sanitization for API routes
 */

import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { validateData } from '@/lib/validation'

/**
 * Validation middleware options
 */
interface ValidationOptions {
  body?: z.ZodSchema
  query?: z.ZodSchema
  params?: z.ZodSchema
  headers?: z.ZodSchema
  skipValidation?: boolean
}

/**
 * Validation result
 */
interface ValidationResult {
  success: boolean
  data?: {
    body?: any
    query?: any
    params?: any
    headers?: any
  }
  errors?: {
    body?: z.ZodError
    query?: z.ZodError
    params?: z.ZodError
    headers?: z.ZodError
  }
}

/**
 * Sanitize string input to prevent XSS and injection attacks
 */
function sanitizeString(input: string): string {
  return input
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+=/gi, '') // Remove event handlers
    .trim()
}

/**
 * Sanitize object recursively
 */
function sanitizeObject(obj: any): any {
  if (typeof obj === 'string') {
    return sanitizeString(obj)
  }
  
  if (Array.isArray(obj)) {
    return obj.map(sanitizeObject)
  }
  
  if (obj && typeof obj === 'object') {
    const sanitized: any = {}
    for (const [key, value] of Object.entries(obj)) {
      sanitized[key] = sanitizeObject(value)
    }
    return sanitized
  }
  
  return obj
}

/**
 * Rate limiting store (in-memory for development)
 */
const rateLimitStore = new Map<string, { count: number; resetTime: number }>()

/**
 * Check rate limit
 */
function checkRateLimit(
  identifier: string,
  limit: number = 100,
  windowMs: number = 15 * 60 * 1000 // 15 minutes
): { allowed: boolean; remaining: number; resetTime: number } {
  const now = Date.now()
  const key = identifier
  const record = rateLimitStore.get(key)
  
  if (!record || now > record.resetTime) {
    // Reset or create new record
    const resetTime = now + windowMs
    rateLimitStore.set(key, { count: 1, resetTime })
    return { allowed: true, remaining: limit - 1, resetTime }
  }
  
  if (record.count >= limit) {
    return { allowed: false, remaining: 0, resetTime: record.resetTime }
  }
  
  record.count++
  return { allowed: true, remaining: limit - record.count, resetTime: record.resetTime }
}

/**
 * Get client identifier for rate limiting
 */
function getClientIdentifier(request: NextRequest): string {
  // Try to get IP address
  const forwarded = request.headers.get('x-forwarded-for')
  const realIp = request.headers.get('x-real-ip')
  const ip = forwarded?.split(',')[0] || realIp || 'unknown'
  
  // Include user agent for additional uniqueness
  const userAgent = request.headers.get('user-agent') || 'unknown'
  
  return `${ip}:${userAgent.slice(0, 50)}`
}

/**
 * Validate request data
 */
export async function validateRequest(
  request: NextRequest,
  options: ValidationOptions
): Promise<ValidationResult> {
  if (options.skipValidation) {
    return { success: true }
  }

  const result: ValidationResult = { success: true, data: {}, errors: {} }
  let hasErrors = false

  try {
    // Validate body
    if (options.body) {
      try {
        const body = await request.json()
        const sanitizedBody = sanitizeObject(body)
        const validation = validateData(options.body, sanitizedBody)
        
        if (validation.success) {
          result.data!.body = validation.data
        } else {
          result.errors!.body = (validation as any).errors
          hasErrors = true
        }
      } catch (error) {
        result.errors!.body = new z.ZodError([
          {
            code: 'custom',
            message: 'Invalid JSON body',
            path: ['body'],
          },
        ])
        hasErrors = true
      }
    }

    // Validate query parameters
    if (options.query) {
      const { searchParams } = new URL(request.url)
      const query = Object.fromEntries(searchParams.entries())
      const sanitizedQuery = sanitizeObject(query)
      const validation = validateData(options.query, sanitizedQuery)
      
      if (validation.success) {
        result.data!.query = validation.data
      } else {
        result.errors!.query = (validation as any).errors
        hasErrors = true
      }
    }

    // Validate headers
    if (options.headers) {
      const headers = Object.fromEntries(request.headers.entries())
      const validation = validateData(options.headers, headers)
      
      if (validation.success) {
        result.data!.headers = validation.data
      } else {
        result.errors!.headers = (validation as any).errors
        hasErrors = true
      }
    }

    result.success = !hasErrors
    return result
  } catch (error) {
    console.error('Validation middleware error:', error)
    return {
      success: false,
      errors: {
        body: new z.ZodError([
          {
            code: 'custom',
            message: 'Validation failed',
            path: ['validation'],
          },
        ]),
      },
    }
  }
}

/**
 * Create validation middleware for API routes
 */
export function createValidationMiddleware(options: ValidationOptions) {
  return async (request: NextRequest) => {
    // Check rate limit
    const clientId = getClientIdentifier(request)
    const rateLimit = checkRateLimit(clientId)
    
    if (!rateLimit.allowed) {
      return NextResponse.json(
        {
          error: 'Too many requests',
          success: false,
          retryAfter: Math.ceil((rateLimit.resetTime - Date.now()) / 1000),
        },
        {
          status: 429,
          headers: {
            'X-RateLimit-Limit': '100',
            'X-RateLimit-Remaining': rateLimit.remaining.toString(),
            'X-RateLimit-Reset': rateLimit.resetTime.toString(),
            'Retry-After': Math.ceil((rateLimit.resetTime - Date.now()) / 1000).toString(),
          },
        }
      )
    }

    // Validate request
    const validation = await validateRequest(request, options)
    
    if (!validation.success) {
      const errorDetails: any = {}
      
      if (validation.errors?.body) {
        errorDetails.body = validation.errors.body.errors
      }
      if (validation.errors?.query) {
        errorDetails.query = validation.errors.query.errors
      }
      if (validation.errors?.headers) {
        errorDetails.headers = validation.errors.headers.errors
      }
      
      return NextResponse.json(
        {
          error: 'Validation failed',
          success: false,
          details: errorDetails,
        },
        { status: 400 }
      )
    }

    // Add validated data to request headers for use in route handlers
    const response = NextResponse.next()
    if (validation.data) {
      response.headers.set('x-validated-data', JSON.stringify(validation.data))
    }
    
    return response
  }
}

/**
 * Security headers middleware
 */
export function addSecurityHeaders(response: NextResponse): NextResponse {
  // Security headers
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-XSS-Protection', '1; mode=block')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
  
  // Content Security Policy
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self'",
    "connect-src 'self' https://api.citypulse.com",
    "frame-ancestors 'none'",
  ].join('; ')
  
  response.headers.set('Content-Security-Policy', csp)
  
  return response
}

/**
 * CORS middleware
 */
export function addCorsHeaders(
  response: NextResponse,
  origin?: string
): NextResponse {
  const allowedOrigins = [
    'http://localhost:3000',
    'https://citypulse.com',
    'https://www.citypulse.com',
  ]
  
  const requestOrigin = origin || '*'
  const isAllowed = allowedOrigins.includes(requestOrigin) || requestOrigin === '*'
  
  if (isAllowed) {
    response.headers.set('Access-Control-Allow-Origin', requestOrigin)
  }
  
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key')
  response.headers.set('Access-Control-Max-Age', '86400')
  
  return response
}

// Export utility functions
export { sanitizeString, sanitizeObject, checkRateLimit, getClientIdentifier }
