/**
 * Events API Client
 * Handles all event-related API operations with service-specific logic
 */

import { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { BaseApiClient } from './base-client'

// Event-related types
export interface Event {
  id?: string
  title: string
  description?: string
  category: string
  severity: string
  status: string
  location: {
    latitude: number
    longitude: number
    address?: string
    city?: string
    state?: string
  }
  user_id?: string
  created_at?: string
  updated_at?: string
  metadata?: Record<string, any>
}

export interface EventFilters {
  category?: string
  severity?: string
  status?: string
  location?: {
    latitude: number
    longitude: number
    radius: number // in kilometers
  }
  dateRange?: {
    start: string
    end: string
  }
  limit?: number
  offset?: number
}

export interface EventsResponse {
  events: Event[]
  total: number
  page: number
  limit: number
  hasMore: boolean
}

export interface EventAnalytics {
  totalEvents: number
  eventsByCategory: Record<string, number>
  eventsBySeverity: Record<string, number>
  eventsByStatus: Record<string, number>
  trendsOverTime: Array<{
    date: string
    count: number
  }>
}

/**
 * Events API Client
 * Provides methods for managing events with enhanced error handling and caching
 */
export class EventsApiClient extends BaseApiClient {
  private cache = new Map<string, { data: any; timestamp: number }>()
  private readonly CACHE_TTL = 5 * 60 * 1000 // 5 minutes

  constructor() {
    super('events', {
      maxRetries: 3,
      retryDelay: 1000,
      retryCondition: (error) => {
        // Retry on network errors and 5xx, but not on 4xx client errors
        return !error.response || error.response.status >= 500
      }
    })
  }

  protected getDefaultHeaders(): Record<string, string> {
    return {
      'X-Client-Version': '1.0.0',
      'X-Feature-Flags': 'events-v2,analytics-enabled'
    }
  }

  protected processRequest(config: AxiosRequestConfig): void {
    // Add request-specific processing for events
    if (config.url?.includes('/events') && config.method?.toLowerCase() === 'get') {
      // Add caching headers for GET requests
      config.headers = {
        ...config.headers,
        'Cache-Control': 'max-age=300' // 5 minutes
      }
    }

    // Add geolocation context if available
    if (typeof navigator !== 'undefined' && navigator.geolocation) {
      // Note: This would need to be handled asynchronously in a real implementation
      config.headers['X-Client-Location'] = 'available'
    }
  }

  protected processResponse(response: AxiosResponse): void {
    // Cache successful GET responses
    if (response.config.method?.toLowerCase() === 'get' && response.status === 200) {
      const cacheKey = this.getCacheKey(response.config.url || '', response.config.params)
      this.cache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now()
      })
    }

    // Log events-specific metrics
    if (response.data?.events) {
      console.log(`[Events] Retrieved ${response.data.events.length} events`)
    }
  }

  protected handleServiceSpecificError(error: AxiosError): void {
    const status = error.response?.status

    switch (status) {
      case 400:
        console.warn('[Events] Bad request - check event data format', {
          correlationId: error.config?.metadata?.correlationId,
          url: error.config?.url
        })
        break
      case 404:
        console.warn('[Events] Event not found', {
          correlationId: error.config?.metadata?.correlationId,
          url: error.config?.url
        })
        break
      case 422:
        console.warn('[Events] Validation error - check required fields', {
          correlationId: error.config?.metadata?.correlationId,
          data: error.response?.data
        })
        break
      default:
        console.error('[Events] Unexpected error', {
          status,
          correlationId: error.config?.metadata?.correlationId
        })
    }
  }

  /**
   * Get events with filtering and caching
   */
  async getEvents(filters?: EventFilters): Promise<EventsResponse> {
    const cacheKey = this.getCacheKey('/events', filters)
    const cached = this.getCachedData(cacheKey)
    
    if (cached) {
      console.log('[Events] Returning cached data')
      return cached
    }

    return this.get<EventsResponse>('/events', { params: filters })
  }

  /**
   * Get a specific event by ID
   */
  async getEvent(id: string): Promise<Event> {
    const cacheKey = this.getCacheKey(`/events/${id}`)
    const cached = this.getCachedData(cacheKey)
    
    if (cached) {
      return cached
    }

    return this.get<Event>(`/events/${id}`)
  }

  /**
   * Create a new event
   */
  async createEvent(event: Omit<Event, 'id' | 'created_at' | 'updated_at'>): Promise<Event> {
    // Clear relevant cache entries
    this.clearCacheByPattern('/events')
    
    return this.post<Event>('/events', event)
  }

  /**
   * Update an existing event
   */
  async updateEvent(id: string, updates: Partial<Event>): Promise<Event> {
    // Clear relevant cache entries
    this.clearCacheByPattern('/events')
    this.cache.delete(this.getCacheKey(`/events/${id}`))
    
    return this.put<Event>(`/events/${id}`, updates)
  }

  /**
   * Delete an event
   */
  async deleteEvent(id: string): Promise<void> {
    // Clear relevant cache entries
    this.clearCacheByPattern('/events')
    this.cache.delete(this.getCacheKey(`/events/${id}`))
    
    return this.delete<void>(`/events/${id}`)
  }

  /**
   * Get events analytics
   */
  async getAnalytics(filters?: Pick<EventFilters, 'dateRange' | 'category' | 'location'>): Promise<EventAnalytics> {
    const cacheKey = this.getCacheKey('/events/analytics', filters)
    const cached = this.getCachedData(cacheKey)
    
    if (cached) {
      return cached
    }

    return this.get<EventAnalytics>('/events/analytics', { params: filters })
  }

  /**
   * Search events by text
   */
  async searchEvents(query: string, filters?: EventFilters): Promise<EventsResponse> {
    const searchParams = { q: query, ...filters }
    return this.get<EventsResponse>('/events/search', { params: searchParams })
  }

  /**
   * Get nearby events based on location
   */
  async getNearbyEvents(latitude: number, longitude: number, radius = 10): Promise<EventsResponse> {
    const params = { latitude, longitude, radius }
    return this.get<EventsResponse>('/events/nearby', { params })
  }

  /**
   * Report an event (citizen reporting)
   */
  async reportEvent(event: Omit<Event, 'id' | 'created_at' | 'updated_at'>, images?: File[]): Promise<Event> {
    if (images && images.length > 0) {
      // Handle file uploads for event reporting
      const formData = new FormData()
      formData.append('event', JSON.stringify(event))
      
      images.forEach((image, index) => {
        formData.append(`image_${index}`, image)
      })

      return this.post<Event>('/events/report', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    } else {
      return this.post<Event>('/events/report', event)
    }
  }

  // Cache management methods
  private getCacheKey(url: string, params?: any): string {
    const paramString = params ? JSON.stringify(params) : ''
    return `${url}:${paramString}`
  }

  private getCachedData(key: string): any | null {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.data
    }
    
    if (cached) {
      this.cache.delete(key) // Remove expired cache
    }
    
    return null
  }

  private clearCacheByPattern(pattern: string): void {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key)
      }
    }
  }

  /**
   * Clear all cached data
   */
  clearCache(): void {
    this.cache.clear()
  }
}

// Export singleton instance
export const eventsApiClient = new EventsApiClient()
