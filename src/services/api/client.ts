import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { APP_CONFIG, STORAGE_KEYS } from '@/utils/constants'

/**
 * API Client for CityPulse application
 * Provides centralized HTTP client with authentication, error handling, and request/response interceptors
 */
class ApiClient {
  private instance: AxiosInstance

  constructor() {
    this.instance = axios.create({
      baseURL: APP_CONFIG.api.baseUrl,
      timeout: APP_CONFIG.api.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = this.getAuthToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // Add request timestamp
        config.metadata = { startTime: new Date() }

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // Log response time
        const endTime = new Date()
        const startTime = response.config.metadata?.startTime
        if (startTime) {
          const duration = endTime.getTime() - startTime.getTime()
          console.log(`API call to ${response.config.url} took ${duration}ms`)
        }

        return response
      },
      (error) => {
        // Handle common errors
        if (error.response?.status === 401) {
          this.handleUnauthorized()
        }

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
    const response = await this.instance.get<T>(url, config)
    return response.data
  }

  /**
   * Perform POST request
   * @param url - Request URL
   * @param data - Request payload
   * @param config - Axios request configuration
   * @returns Promise resolving to response data
   */
  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post<T>(url, data, config)
    return response.data
  }

  /**
   * Perform PUT request
   * @param url - Request URL
   * @param data - Request payload
   * @param config - Axios request configuration
   * @returns Promise resolving to response data
   */
  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.put<T>(url, data, config)
    return response.data
  }

  /**
   * Perform PATCH request
   * @param url - Request URL
   * @param data - Request payload
   * @param config - Axios request configuration
   * @returns Promise resolving to response data
   */
  async patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.patch<T>(url, data, config)
    return response.data
  }

  /**
   * Perform DELETE request
   * @param url - Request URL
   * @param config - Axios request configuration
   * @returns Promise resolving to response data
   */
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.delete<T>(url, config)
    return response.data
  }

  // File upload
  async uploadFile<T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData()
    formData.append('file', file)

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    }

    const response = await this.instance.post<T>(url, formData, config)
    return response.data
  }

  // Batch requests
  async batch<T>(requests: Array<() => Promise<T>>): Promise<(T | null)[]> {
    const responses = await Promise.allSettled(requests.map(request => request()))
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
      startTime: Date
    }
  }
}
