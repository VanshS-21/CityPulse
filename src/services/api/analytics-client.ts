/**
 * Analytics API Client
 * Handles all analytics and reporting API operations with caching and aggregation
 */

import { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { BaseApiClient } from './base-client'

// Analytics-related types
export interface TimeRange {
  start: string // ISO date string
  end: string   // ISO date string
}

export interface MetricFilter {
  timeRange?: TimeRange
  category?: string
  severity?: string
  location?: {
    latitude: number
    longitude: number
    radius: number
  }
  groupBy?: 'day' | 'week' | 'month' | 'category' | 'severity' | 'location'
}

export interface MetricData {
  timestamp: string
  value: number
  metadata?: Record<string, any>
}

export interface AggregatedMetric {
  name: string
  value: number
  change: number // percentage change from previous period
  trend: 'up' | 'down' | 'stable'
  data: MetricData[]
}

export interface DashboardMetrics {
  totalEvents: AggregatedMetric
  activeEvents: AggregatedMetric
  resolvedEvents: AggregatedMetric
  averageResolutionTime: AggregatedMetric
  userEngagement: AggregatedMetric
  topCategories: Array<{
    category: string
    count: number
    percentage: number
  }>
  geographicDistribution: Array<{
    location: string
    count: number
    coordinates: [number, number]
  }>
}

export interface ReportConfig {
  title: string
  description?: string
  timeRange: TimeRange
  metrics: string[]
  filters?: MetricFilter
  format: 'json' | 'csv' | 'pdf'
  schedule?: {
    frequency: 'daily' | 'weekly' | 'monthly'
    recipients: string[]
  }
}

export interface Report {
  id: string
  config: ReportConfig
  status: 'pending' | 'generating' | 'completed' | 'failed'
  created_at: string
  completed_at?: string
  download_url?: string
  error_message?: string
}

/**
 * Analytics API Client
 * Provides methods for retrieving analytics data with intelligent caching and performance optimization
 */
export class AnalyticsApiClient extends BaseApiClient {
  private metricsCache = new Map<string, { data: any; timestamp: number }>()
  private readonly CACHE_TTL = 15 * 60 * 1000 // 15 minutes for analytics data
  private readonly DASHBOARD_CACHE_TTL = 5 * 60 * 1000 // 5 minutes for dashboard

  constructor() {
    super('analytics', {
      maxRetries: 2,
      retryDelay: 2000,
      retryCondition: (error) => {
        // Analytics queries can be expensive, be conservative with retries
        return !error.response || error.response.status >= 500
      }
    })
  }

  protected getDefaultHeaders(): Record<string, string> {
    return {
      'X-Client-Version': '1.0.0',
      'X-Analytics-Client': 'web',
      'X-Cache-Strategy': 'aggressive'
    }
  }

  protected processRequest(config: AxiosRequestConfig): void {
    // Add analytics-specific headers
    config.headers = {
      ...config.headers,
      'X-Request-Type': 'analytics-query'
    }

    // Add query optimization hints
    if (config.url?.includes('/dashboard')) {
      config.headers['X-Query-Priority'] = 'high'
    } else if (config.url?.includes('/reports')) {
      config.headers['X-Query-Priority'] = 'low'
      config.timeout = 30000 // Longer timeout for report generation
    }

    // Add caching preferences
    if (config.method?.toLowerCase() === 'get') {
      config.headers['X-Cache-Preference'] = 'prefer-cache'
    }
  }

  protected processResponse(response: AxiosResponse): void {
    // Cache analytics responses aggressively
    if (response.config.method?.toLowerCase() === 'get' && response.status === 200) {
      const cacheKey = this.getCacheKey(response.config.url || '', response.config.params)
      const ttl = response.config.url?.includes('/dashboard') ? this.DASHBOARD_CACHE_TTL : this.CACHE_TTL
      
      this.metricsCache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now()
      })

      // Set cache expiry
      setTimeout(() => {
        this.metricsCache.delete(cacheKey)
      }, ttl)
    }

    // Log analytics query performance
    const metadata = response.config.metadata
    if (metadata) {
      const duration = Date.now() - metadata.startTime
      console.log(`[Analytics] Query completed`, {
        correlationId: metadata.correlationId,
        duration: `${duration}ms`,
        cacheHit: response.headers['x-cache-status'] === 'hit',
        dataPoints: this.estimateDataPoints(response.data)
      })

      // Warn about slow queries
      if (duration > 10000) {
        console.warn(`[Analytics] Slow query detected`, {
          correlationId: metadata.correlationId,
          duration: `${duration}ms`,
          url: response.config.url
        })
      }
    }
  }

  protected handleServiceSpecificError(error: AxiosError): void {
    const status = error.response?.status

    switch (status) {
      case 400:
        console.warn('[Analytics] Invalid query parameters', {
          correlationId: error.config?.metadata?.correlationId,
          params: error.config?.params
        })
        break
      case 413:
        console.warn('[Analytics] Query result too large', {
          correlationId: error.config?.metadata?.correlationId,
          suggestion: 'Try reducing the time range or adding more filters'
        })
        break
      case 429:
        console.warn('[Analytics] Rate limit exceeded', {
          correlationId: error.config?.metadata?.correlationId,
          retryAfter: error.response?.headers['retry-after']
        })
        break
      case 503:
        console.warn('[Analytics] Analytics service temporarily unavailable', {
          correlationId: error.config?.metadata?.correlationId
        })
        break
      default:
        console.error('[Analytics] Unexpected analytics error', {
          status,
          correlationId: error.config?.metadata?.correlationId
        })
    }
  }

  /**
   * Get dashboard metrics with caching
   */
  async getDashboardMetrics(filters?: MetricFilter): Promise<DashboardMetrics> {
    const cacheKey = this.getCacheKey('/analytics/dashboard', filters)
    const cached = this.getCachedData(cacheKey, this.DASHBOARD_CACHE_TTL)
    
    if (cached) {
      console.log('[Analytics] Returning cached dashboard metrics')
      return cached
    }

    return this.get<DashboardMetrics>('/analytics/dashboard', { params: filters })
  }

  /**
   * Get specific metric data
   */
  async getMetric(metricName: string, filters?: MetricFilter): Promise<AggregatedMetric> {
    const cacheKey = this.getCacheKey(`/analytics/metrics/${metricName}`, filters)
    const cached = this.getCachedData(cacheKey)
    
    if (cached) {
      return cached
    }

    return this.get<AggregatedMetric>(`/analytics/metrics/${metricName}`, { params: filters })
  }

  /**
   * Get multiple metrics in a single request
   */
  async getMetrics(metricNames: string[], filters?: MetricFilter): Promise<Record<string, AggregatedMetric>> {
    const params = { metrics: metricNames.join(','), ...filters }
    return this.get<Record<string, AggregatedMetric>>('/analytics/metrics/batch', { params })
  }

  /**
   * Get time series data for a metric
   */
  async getTimeSeries(metricName: string, filters?: MetricFilter): Promise<MetricData[]> {
    const cacheKey = this.getCacheKey(`/analytics/timeseries/${metricName}`, filters)
    const cached = this.getCachedData(cacheKey)
    
    if (cached) {
      return cached
    }

    return this.get<MetricData[]>(`/analytics/timeseries/${metricName}`, { params: filters })
  }

  /**
   * Get geographic analytics data
   */
  async getGeographicAnalytics(filters?: MetricFilter): Promise<Array<{
    location: string
    coordinates: [number, number]
    metrics: Record<string, number>
  }>> {
    return this.get('/analytics/geographic', { params: filters })
  }

  /**
   * Create a custom report
   */
  async createReport(config: ReportConfig): Promise<Report> {
    return this.post<Report>('/analytics/reports', config)
  }

  /**
   * Get report status
   */
  async getReport(reportId: string): Promise<Report> {
    return this.get<Report>(`/analytics/reports/${reportId}`)
  }

  /**
   * Get list of reports
   */
  async getReports(limit = 20, offset = 0): Promise<{
    reports: Report[]
    total: number
    hasMore: boolean
  }> {
    return this.get('/analytics/reports', { params: { limit, offset } })
  }

  /**
   * Download report data
   */
  async downloadReport(reportId: string): Promise<Blob> {
    const response = await this.instance.get(`/analytics/reports/${reportId}/download`, {
      responseType: 'blob'
    })
    return response.data
  }

  /**
   * Delete a report
   */
  async deleteReport(reportId: string): Promise<void> {
    return this.delete<void>(`/analytics/reports/${reportId}`)
  }

  /**
   * Get available metrics list
   */
  async getAvailableMetrics(): Promise<Array<{
    name: string
    description: string
    category: string
    dataType: string
  }>> {
    const cacheKey = 'available-metrics'
    const cached = this.getCachedData(cacheKey, 60 * 60 * 1000) // Cache for 1 hour
    
    if (cached) {
      return cached
    }

    return this.get<Array<{
      name: string
      description: string
      category: string
      dataType: string
    }>>('/analytics/metrics/available')
  }

  /**
   * Refresh analytics data (force cache invalidation)
   */
  async refreshAnalytics(): Promise<void> {
    this.clearCache()
    return this.post<void>('/analytics/refresh')
  }

  // Cache management methods
  private getCacheKey(url: string, params?: any): string {
    const paramString = params ? JSON.stringify(params) : ''
    return `${url}:${paramString}`
  }

  private getCachedData(key: string, customTTL?: number): any | null {
    const cached = this.metricsCache.get(key)
    const ttl = customTTL || this.CACHE_TTL
    
    if (cached && Date.now() - cached.timestamp < ttl) {
      return cached.data
    }
    
    if (cached) {
      this.metricsCache.delete(key)
    }
    
    return null
  }

  private estimateDataPoints(data: any): number {
    if (Array.isArray(data)) {
      return data.length
    }
    if (data?.data && Array.isArray(data.data)) {
      return data.data.length
    }
    return 1
  }

  /**
   * Clear analytics cache
   */
  clearCache(): void {
    this.metricsCache.clear()
    console.log('[Analytics] Cache cleared')
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.metricsCache.size,
      keys: Array.from(this.metricsCache.keys())
    }
  }
}

// Export singleton instance
export const analyticsApiClient = new AnalyticsApiClient()
