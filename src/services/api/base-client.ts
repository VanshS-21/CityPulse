/**
 * Enhanced Base API Client for CityPulse application
 * Provides consistent error handling, correlation tracking, and service-specific patterns
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { APP_CONFIG, STORAGE_KEYS } from '@/utils/constants'

// Types for enhanced error handling
export interface ApiError {
  message: string
  code: string
  correlationId?: string
  details?: Record<string, any>
  statusCode: number
}

export interface RequestMetadata {
  startTime: number
  requestId: string
  correlationId: string
  service: string
  operation?: string
}

export interface RetryConfig {
  maxRetries: number
  retryDelay: number
  retryCondition?: (error: AxiosError) => boolean
}

/**
 * Abstract base class for all API clients
 * Provides common functionality and enforces consistent patterns
 */
export abstract class BaseApiClient {
  protected instance: AxiosInstance
  protected serviceName: string
  protected retryConfig: RetryConfig

  constructor(serviceName: string, retryConfig?: Partial<RetryConfig>) {
    this.serviceName = serviceName
    this.retryConfig = {
      maxRetries: 3,
      retryDelay: 1000,
      retryCondition: this.defaultRetryCondition,
      ...retryConfig
    }
    
    this.instance = this.createInstance()
    this.setupInterceptors()
  }

  /**
   * Create the axios instance with service-specific configuration
   */
  private createInstance(): AxiosInstance {
    return axios.create({
      baseURL: APP_CONFIG.api.baseUrl,
      timeout: APP_CONFIG.api.timeout,
      headers: {
        'Content-Type': 'application/json',
        'X-Service': this.serviceName,
        ...this.getDefaultHeaders(),
      },
    })
  }

  /**
   * Setup request and response interceptors
   */
  private setupInterceptors(): void {
    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        const correlationId = this.generateCorrelationId()
        const requestId = this.generateRequestId()
        
        // Add authentication
        const token = this.getAuthToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // Add correlation tracking
        config.headers['X-Correlation-ID'] = correlationId
        config.headers['X-Request-ID'] = requestId

        // Add metadata for tracking
        config.metadata = {
          startTime: Date.now(),
          requestId,
          correlationId,
          service: this.serviceName,
          operation: this.extractOperationFromUrl(config.url || '')
        }

        // Service-specific request processing
        this.processRequest(config)

        return config
      },
      (error) => {
        return Promise.reject(this.createApiError(error, 'REQUEST_SETUP_ERROR'))
      }
    )

    // Response interceptor
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        this.logResponseMetrics(response)
        this.processResponse(response)
        return response
      },
      async (error: AxiosError) => {
        return this.handleResponseError(error)
      }
    )
  }

  /**
   * Handle response errors with retry logic and service-specific handling
   */
  private async handleResponseError(error: AxiosError): Promise<never> {
    const config = error.config as AxiosRequestConfig & { _retryCount?: number }
    
    // Check if we should retry
    if (this.shouldRetry(error, config)) {
      config._retryCount = (config._retryCount || 0) + 1
      
      // Wait before retrying
      await this.delay(this.retryConfig.retryDelay * config._retryCount)
      
      try {
        return await this.instance.request(config)
      } catch (retryError) {
        // If retry fails, continue with original error handling
        error = retryError as AxiosError
      }
    }

    // Handle specific error types
    if (error.response?.status === 401) {
      this.handleUnauthorized(error)
    }

    // Service-specific error handling
    this.handleServiceSpecificError(error)

    // Create and throw enhanced API error
    throw this.createApiError(error)
  }

  /**
   * Determine if a request should be retried
   */
  private shouldRetry(error: AxiosError, config: AxiosRequestConfig & { _retryCount?: number }): boolean {
    const retryCount = config._retryCount || 0
    
    if (retryCount >= this.retryConfig.maxRetries) {
      return false
    }

    if (this.retryConfig.retryCondition) {
      return this.retryConfig.retryCondition(error)
    }

    return false
  }

  /**
   * Default retry condition - retry on network errors and 5xx responses
   */
  private defaultRetryCondition(error: AxiosError): boolean {
    return !error.response || (error.response.status >= 500 && error.response.status < 600)
  }

  /**
   * Create enhanced API error with correlation tracking
   */
  private createApiError(error: AxiosError, defaultCode = 'API_ERROR'): ApiError {
    const correlationId = error.config?.metadata?.correlationId
    const statusCode = error.response?.status || 0
    
    let message = 'An error occurred'
    let code = defaultCode
    let details: Record<string, any> = {}

    if (error.response?.data) {
      const responseData = error.response.data as any
      message = responseData.message || responseData.detail?.message || message
      code = responseData.code || responseData.detail?.error_code || code
      details = responseData.details || responseData.detail?.details || {}
    } else if (error.message) {
      message = error.message
    }

    return {
      message,
      code,
      correlationId,
      details,
      statusCode
    }
  }

  /**
   * Log response metrics for monitoring
   */
  private logResponseMetrics(response: AxiosResponse): void {
    const metadata = response.config.metadata
    if (metadata) {
      const duration = Date.now() - metadata.startTime
      
      console.log(`[${this.serviceName}] ${metadata.operation || 'API'} call completed`, {
        correlationId: metadata.correlationId,
        requestId: metadata.requestId,
        duration: `${duration}ms`,
        status: response.status,
        url: response.config.url
      })

      // Performance monitoring
      if (duration > 5000) {
        console.warn(`[${this.serviceName}] Slow API call detected`, {
          correlationId: metadata.correlationId,
          duration: `${duration}ms`,
          url: response.config.url
        })
      }
    }
  }

  /**
   * Extract operation name from URL for better logging
   */
  private extractOperationFromUrl(url: string): string {
    const parts = url.split('/').filter(Boolean)
    return parts[parts.length - 1] || 'unknown'
  }

  /**
   * Generate correlation ID for request tracking
   */
  private generateCorrelationId(): string {
    return `${this.serviceName}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Generate request ID
   */
  private generateRequestId(): string {
    return Math.random().toString(36).substr(2, 9)
  }

  /**
   * Get authentication token
   */
  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.authToken)
    }
    return null
  }

  /**
   * Handle unauthorized responses
   */
  private handleUnauthorized(error: AxiosError): void {
    console.warn(`[${this.serviceName}] Unauthorized request`, {
      correlationId: error.config?.metadata?.correlationId,
      url: error.config?.url
    })

    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEYS.authToken)
      // Don't redirect immediately, let the application handle it
      window.dispatchEvent(new CustomEvent('auth:unauthorized', { 
        detail: { correlationId: error.config?.metadata?.correlationId }
      }))
    }
  }

  /**
   * Delay utility for retry logic
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  // Abstract methods that must be implemented by service-specific clients
  protected abstract getDefaultHeaders(): Record<string, string>
  protected abstract processRequest(config: AxiosRequestConfig): void
  protected abstract processResponse(response: AxiosResponse): void
  protected abstract handleServiceSpecificError(error: AxiosError): void

  // Common HTTP methods with enhanced error handling
  protected async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get<T>(url, config)
    return response.data
  }

  protected async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post<T>(url, data, config)
    return response.data
  }

  protected async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.put<T>(url, data, config)
    return response.data
  }

  protected async patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.patch<T>(url, data, config)
    return response.data
  }

  protected async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.delete<T>(url, config)
    return response.data
  }
}

// Extend Axios types for our metadata
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: RequestMetadata
  }
}
