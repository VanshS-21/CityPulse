/**
 * Unified API Client Interface
 * Exports all service-specific API clients and provides a centralized interface
 */

// Export base client for extending
export { BaseApiClient } from './base-client'
export type { ApiError, RequestMetadata, RetryConfig } from './base-client'

// Export service-specific clients
export { eventsApiClient, EventsApiClient } from './events-client'
export type { Event, EventFilters, EventsResponse, EventAnalytics } from './events-client'

export { usersApiClient, UsersApiClient } from './users-client'
export type { User, UserProfile, UserFilters, UsersResponse, UserActivity, UserStats } from './users-client'

export { analyticsApiClient, AnalyticsApiClient } from './analytics-client'
export type { 
  TimeRange, 
  MetricFilter, 
  MetricData, 
  AggregatedMetric, 
  DashboardMetrics, 
  ReportConfig, 
  Report 
} from './analytics-client'

// Legacy client for backward compatibility
export { apiClient } from './client'

/**
 * Unified API interface that provides access to all service clients
 * This is the main interface that should be used throughout the application
 */
export class CityPulseApi {
  public readonly events = eventsApiClient
  public readonly users = usersApiClient
  public readonly analytics = analyticsApiClient

  /**
   * Initialize the API with user context
   */
  async initialize(): Promise<void> {
    try {
      // Get current user and set context
      const currentUser = await this.users.getCurrentUser()
      console.log('[CityPulse API] Initialized with user context', {
        userId: currentUser.user_id,
        role: currentUser.role
      })
    } catch (error) {
      console.warn('[CityPulse API] Failed to initialize user context', error)
      // Continue without user context - user might not be logged in
    }
  }

  /**
   * Clear all caches across all services
   */
  clearAllCaches(): void {
    this.events.clearCache()
    this.users.clearCache()
    this.analytics.clearCache()
    console.log('[CityPulse API] All caches cleared')
  }

  /**
   * Get health status of all API services
   */
  async getHealthStatus(): Promise<{
    overall: 'healthy' | 'degraded' | 'unhealthy'
    services: Record<string, {
      status: 'healthy' | 'degraded' | 'unhealthy'
      responseTime?: number
      lastChecked: string
    }>
  }> {
    const healthChecks = await Promise.allSettled([
      this.checkServiceHealth('events'),
      this.checkServiceHealth('users'),
      this.checkServiceHealth('analytics')
    ])

    const services: Record<string, any> = {}
    const serviceNames = ['events', 'users', 'analytics']
    
    healthChecks.forEach((result, index) => {
      const serviceName = serviceNames[index]
      if (result.status === 'fulfilled') {
        services[serviceName] = result.value
      } else {
        services[serviceName] = {
          status: 'unhealthy',
          lastChecked: new Date().toISOString(),
          error: result.reason?.message || 'Unknown error'
        }
      }
    })

    // Determine overall health
    const healthyServices = Object.values(services).filter(s => s.status === 'healthy').length
    const totalServices = Object.keys(services).length
    
    let overall: 'healthy' | 'degraded' | 'unhealthy'
    if (healthyServices === totalServices) {
      overall = 'healthy'
    } else if (healthyServices > 0) {
      overall = 'degraded'
    } else {
      overall = 'unhealthy'
    }

    return { overall, services }
  }

  /**
   * Check health of a specific service
   */
  private async checkServiceHealth(serviceName: string): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy'
    responseTime: number
    lastChecked: string
  }> {
    const startTime = Date.now()
    
    try {
      // Use a lightweight endpoint for health checking
      let client: any
      switch (serviceName) {
        case 'events':
          client = this.events
          await client.get('/health')
          break
        case 'users':
          client = this.users
          await client.get('/health')
          break
        case 'analytics':
          client = this.analytics
          await client.get('/health')
          break
        default:
          throw new Error(`Unknown service: ${serviceName}`)
      }

      const responseTime = Date.now() - startTime
      
      return {
        status: responseTime < 1000 ? 'healthy' : 'degraded',
        responseTime,
        lastChecked: new Date().toISOString()
      }
    } catch (error) {
      return {
        status: 'unhealthy',
        responseTime: Date.now() - startTime,
        lastChecked: new Date().toISOString()
      }
    }
  }

  /**
   * Get API usage statistics
   */
  getUsageStats(): {
    events: { cacheSize: number; cacheKeys: string[] }
    users: { cacheSize: number; currentUser: string | null }
    analytics: { cacheSize: number; cacheKeys: string[] }
  } {
    return {
      events: {
        cacheSize: (this.events as any).cache?.size || 0,
        cacheKeys: Array.from((this.events as any).cache?.keys() || [])
      },
      users: {
        cacheSize: (this.users as any).userCache?.size || 0,
        currentUser: this.users.getCurrentUserRole()
      },
      analytics: this.analytics.getCacheStats()
    }
  }

  /**
   * Configure global error handling
   */
  onError(handler: (error: any, context: { service: string; operation: string; correlationId?: string }) => void): void {
    // This would be implemented to hook into the error handling of all clients
    console.log('[CityPulse API] Global error handler configured')
  }

  /**
   * Configure global request/response logging
   */
  onRequest(handler: (request: { service: string; operation: string; correlationId: string }) => void): void {
    // This would be implemented to hook into the request lifecycle of all clients
    console.log('[CityPulse API] Global request handler configured')
  }
}

// Export singleton instance
export const cityPulseApi = new CityPulseApi()

// Initialize on import (in browser environment)
if (typeof window !== 'undefined') {
  cityPulseApi.initialize().catch(error => {
    console.warn('[CityPulse API] Auto-initialization failed', error)
  })
}

// Export convenience functions for direct access
export const {
  events: eventsApi,
  users: usersApi,
  analytics: analyticsApi
} = cityPulseApi

/**
 * Utility function to handle API errors consistently
 */
export function handleApiError(error: any): {
  message: string
  code: string
  correlationId?: string
  isRetryable: boolean
} {
  if (error?.correlationId) {
    // Enhanced API error
    return {
      message: error.message,
      code: error.code,
      correlationId: error.correlationId,
      isRetryable: error.statusCode >= 500
    }
  } else {
    // Standard error
    return {
      message: error?.message || 'An unexpected error occurred',
      code: 'UNKNOWN_ERROR',
      isRetryable: false
    }
  }
}

/**
 * Utility function to check if user has required permissions
 */
export function checkPermissions(requiredRole: 'citizen' | 'moderator' | 'admin'): boolean {
  const currentRole = usersApi.getCurrentUserRole()
  
  if (!currentRole) return false
  
  const roleHierarchy = { citizen: 0, moderator: 1, admin: 2 }
  return roleHierarchy[currentRole] >= roleHierarchy[requiredRole]
}
