import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { APP_CONFIG, STORAGE_KEYS } from '@/utils/constants'
import { createErrorBoundaryInfo } from '@/lib/error-handler'
import { config } from '@/lib/config'

/**
 * API Client for CityPulse application
 * Provides centralized HTTP client with authentication, error handling, and request/response interceptors
 */
class ApiClient {
  private instance: AxiosInstance

  constructor() {
    this.instance = axios.create({
      baseURL: APP_CONFIG.api.baseUrl,
      timeout: config.api.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.instance.interceptors.request.use(
      config => {
        // Add auth token if available
        const token = this.getAuthToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // Add request timestamp
        config.metadata = {
          startTime: Date.now(),
          requestId: Math.random().toString(36).substr(2, 9),
        }

        return config
      },
      error => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // Log response time
        const endTime = Date.now()
        const startTime = response.config.metadata?.startTime
        if (startTime) {
          const duration = endTime - startTime
          console.log(`API call to ${response.config.url} took ${duration}ms`)
        }

        return response
      },
      error => {
        // Handle specific error cases
        if (error.response?.status === 401) {
          this.handleUnauthorized()
        }

        // Log error for monitoring
        console.error('API Error:', {
          url: error.config?.url,
          method: error.config?.method,
          requestId: error.config?.metadata?.requestId,
          status: error.response?.status,
          message: error.message,
        })

        return Promise.reject(error)
      }
    )
  }

  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.authToken)
    }
    return null
  }

  private handleUnauthorized() {
    // Clear auth token and redirect to login
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEYS.authToken)
      window.location.href = '/auth/login'
    }
  }

  // HTTP methods
  /**
   * Perform GET request
   * @param url - Request URL
   * @param config - Axios request configuration
   * @returns Promise resolving to response data
   */
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry(() => this.instance.get<T>(url, config))
  }

  /**
   * Perform POST request
   * @param url - Request URL
   * @param data - Request payload
   * @param config - Axios request configuration
   * @returns Promise resolving to response data
   */
  async post<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.requestWithRetry(() => this.instance.post<T>(url, data, config))
  }

  /**
   * Perform PUT request
   * @param url - Request URL
   * @param data - Request payload
   * @param config - Axios request configuration
   * @returns Promise resolving to response data
   */
  async put<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.requestWithRetry(() => this.instance.put<T>(url, data, config))
  }

  /**
   * Perform PATCH request
   * @param url - Request URL
   * @param data - Request payload
   * @param config - Axios request configuration
   * @returns Promise resolving to response data
   */
  async patch<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.requestWithRetry(() =>
      this.instance.patch<T>(url, data, config)
    )
  }

  /**
   * Perform DELETE request
   * @param url - Request URL
   * @param config - Axios request configuration
   * @returns Promise resolving to response data
   */
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry(() => this.instance.delete<T>(url, config))
  }

  // File upload with enhanced timeout
  async uploadFile<T>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData()
    formData.append('file', file)

    const uploadTimeout = config.api.timeout * 2 // Double timeout for uploads
    const requestConfig: AxiosRequestConfig = {
      timeout: uploadTimeout,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: progressEvent => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onProgress(progress)
        }
      },
    }

    return this.requestWithRetry(() =>
      this.instance.post<T>(url, formData, requestConfig)
    )
  }

  // Private method for request with retry logic
  private async requestWithRetry<T>(
    requestFn: () => Promise<AxiosResponse<T>>
  ): Promise<T> {
    const maxRetries = 3
    let lastError: Error

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        const response = await requestFn()
        return response.data
      } catch (error) {
        lastError = error as Error

        // Don't retry on 4xx errors (client errors)
        if (
          axios.isAxiosError(error) &&
          error.response?.status &&
          error.response.status >= 400 &&
          error.response.status < 500
        ) {
          throw error
        }

        // Wait before retrying (exponential backoff)
        if (attempt < maxRetries - 1) {
          await new Promise(resolve =>
            setTimeout(resolve, Math.pow(2, attempt) * 1000)
          )
        }
      }
    }

    throw lastError!
  }

  // Batch requests
  async batch<T>(requests: Array<() => Promise<T>>): Promise<(T | null)[]> {
    const responses = await Promise.allSettled(
      requests.map(request => request())
    )
    return responses.map(response =>
      response.status === 'fulfilled' ? response.value : null
    )
  }
}

// Create and export singleton instance
export const apiClient = new ApiClient()

// Export types for TypeScript
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      startTime: number
      requestId: string
    }
  }
}
