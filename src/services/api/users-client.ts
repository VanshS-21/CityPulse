/**
 * Users API Client
 * Handles all user-related API operations with service-specific logic
 */

import { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { BaseApiClient } from './base-client'

// User-related types
export interface User {
  user_id: string
  email: string
  display_name?: string
  role: 'citizen' | 'admin' | 'moderator'
  is_active: boolean
  created_at?: string
  updated_at?: string
  metadata?: Record<string, any>
}

export interface UserProfile extends User {
  phone?: string
  location?: {
    latitude: number
    longitude: number
    address?: string
    city?: string
    state?: string
  }
  notification_preferences?: {
    email: boolean
    push: boolean
    sms: boolean
  }
  preferences?: Record<string, any>
}

export interface UserFilters {
  role?: string
  is_active?: boolean
  search?: string
  limit?: number
  offset?: number
}

export interface UsersResponse {
  users: User[]
  total: number
  page: number
  limit: number
  hasMore: boolean
}

export interface UserActivity {
  user_id: string
  activity_type: string
  description: string
  timestamp: string
  metadata?: Record<string, any>
}

export interface UserStats {
  total_users: number
  active_users: number
  users_by_role: Record<string, number>
  recent_signups: number
  activity_summary: {
    events_reported: number
    feedback_submitted: number
    last_active: string
  }
}

/**
 * Users API Client
 * Provides methods for managing users with role-based access and privacy controls
 */
export class UsersApiClient extends BaseApiClient {
  private currentUser: UserProfile | null = null
  private userCache = new Map<string, { user: UserProfile; timestamp: number }>()
  private readonly CACHE_TTL = 10 * 60 * 1000 // 10 minutes

  constructor() {
    super('users', {
      maxRetries: 2,
      retryDelay: 1500,
      retryCondition: (error) => {
        // Be more conservative with retries for user operations
        return !error.response || (error.response.status >= 500 && error.response.status !== 503)
      }
    })
  }

  protected getDefaultHeaders(): Record<string, string> {
    return {
      'X-Client-Version': '1.0.0',
      'X-Privacy-Level': 'standard',
      'X-Data-Classification': 'pii' // Personal Identifiable Information
    }
  }

  protected processRequest(config: AxiosRequestConfig): void {
    // Add privacy and security headers for user operations
    config.headers = {
      ...config.headers,
      'X-Request-Type': 'user-operation'
    }

    // Add user context if available
    if (this.currentUser) {
      config.headers['X-Current-User-Role'] = this.currentUser.role
      config.headers['X-Current-User-ID'] = this.currentUser.user_id
    }

    // Ensure sensitive operations have proper headers
    if (config.url?.includes('/profile') || config.url?.includes('/preferences')) {
      config.headers['X-Sensitive-Operation'] = 'true'
    }
  }

  protected processResponse(response: AxiosResponse): void {
    // Cache user profiles for performance
    if (response.config.url?.includes('/users/') && response.config.method?.toLowerCase() === 'get') {
      const userData = response.data as UserProfile
      if (userData.user_id) {
        this.userCache.set(userData.user_id, {
          user: userData,
          timestamp: Date.now()
        })
      }
    }

    // Log user operation metrics (without sensitive data)
    if (response.data?.user_id || response.data?.users) {
      const userCount = response.data.users?.length || 1
      console.log(`[Users] Operation completed for ${userCount} user(s)`, {
        correlationId: response.config.metadata?.correlationId,
        operation: response.config.metadata?.operation
      })
    }
  }

  protected handleServiceSpecificError(error: AxiosError): void {
    const status = error.response?.status

    switch (status) {
      case 400:
        console.warn('[Users] Invalid user data provided', {
          correlationId: error.config?.metadata?.correlationId
        })
        break
      case 403:
        console.warn('[Users] Insufficient permissions for user operation', {
          correlationId: error.config?.metadata?.correlationId,
          currentUserRole: this.currentUser?.role
        })
        break
      case 404:
        console.warn('[Users] User not found', {
          correlationId: error.config?.metadata?.correlationId
        })
        break
      case 409:
        console.warn('[Users] User conflict (email already exists)', {
          correlationId: error.config?.metadata?.correlationId
        })
        break
      case 422:
        console.warn('[Users] User validation failed', {
          correlationId: error.config?.metadata?.correlationId,
          validationErrors: error.response?.data
        })
        break
      default:
        console.error('[Users] Unexpected user operation error', {
          status,
          correlationId: error.config?.metadata?.correlationId
        })
    }
  }

  /**
   * Set current user context for enhanced security and logging
   */
  setCurrentUser(user: UserProfile): void {
    this.currentUser = user
    console.log('[Users] Current user context set', {
      userId: user.user_id,
      role: user.role
    })
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<UserProfile> {
    if (this.currentUser) {
      // Check if we have fresh cached data
      const cached = this.userCache.get(this.currentUser.user_id)
      if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
        return cached.user
      }
    }

    const user = await this.get<UserProfile>('/users/me')
    this.setCurrentUser(user)
    return user
  }

  /**
   * Get users with filtering (admin/moderator only)
   */
  async getUsers(filters?: UserFilters): Promise<UsersResponse> {
    return this.get<UsersResponse>('/users', { params: filters })
  }

  /**
   * Get a specific user by ID
   */
  async getUser(userId: string): Promise<UserProfile> {
    // Check cache first
    const cached = this.userCache.get(userId)
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.user
    }

    return this.get<UserProfile>(`/users/${userId}`)
  }

  /**
   * Update user profile
   */
  async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    // Clear cache for current user
    if (this.currentUser) {
      this.userCache.delete(this.currentUser.user_id)
    }

    const updatedUser = await this.put<UserProfile>('/users/me', updates)
    this.setCurrentUser(updatedUser)
    return updatedUser
  }

  /**
   * Update user preferences
   */
  async updatePreferences(preferences: Record<string, any>): Promise<UserProfile> {
    if (this.currentUser) {
      this.userCache.delete(this.currentUser.user_id)
    }

    return this.patch<UserProfile>('/users/me/preferences', { preferences })
  }

  /**
   * Update notification preferences
   */
  async updateNotificationPreferences(notificationPreferences: UserProfile['notification_preferences']): Promise<UserProfile> {
    if (this.currentUser) {
      this.userCache.delete(this.currentUser.user_id)
    }

    return this.patch<UserProfile>('/users/me/notifications', { notification_preferences: notificationPreferences })
  }

  /**
   * Get user activity history
   */
  async getUserActivity(userId?: string, limit = 50): Promise<UserActivity[]> {
    const targetUserId = userId || this.currentUser?.user_id
    if (!targetUserId) {
      throw new Error('User ID required for activity history')
    }

    return this.get<UserActivity[]>(`/users/${targetUserId}/activity`, {
      params: { limit }
    })
  }

  /**
   * Get user statistics (admin only)
   */
  async getUserStats(): Promise<UserStats> {
    return this.get<UserStats>('/users/stats')
  }

  /**
   * Search users by email or name (admin/moderator only)
   */
  async searchUsers(query: string, limit = 20): Promise<UsersResponse> {
    return this.get<UsersResponse>('/users/search', {
      params: { q: query, limit }
    })
  }

  /**
   * Deactivate user account
   */
  async deactivateUser(userId: string): Promise<void> {
    this.userCache.delete(userId)
    return this.patch<void>(`/users/${userId}/deactivate`)
  }

  /**
   * Reactivate user account
   */
  async reactivateUser(userId: string): Promise<void> {
    this.userCache.delete(userId)
    return this.patch<void>(`/users/${userId}/reactivate`)
  }

  /**
   * Update user role (admin only)
   */
  async updateUserRole(userId: string, role: User['role']): Promise<UserProfile> {
    this.userCache.delete(userId)
    return this.patch<UserProfile>(`/users/${userId}/role`, { role })
  }

  /**
   * Delete user account (admin only)
   */
  async deleteUser(userId: string): Promise<void> {
    this.userCache.delete(userId)
    return this.delete<void>(`/users/${userId}`)
  }

  /**
   * Upload user avatar
   */
  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData()
    formData.append('avatar', file)

    return this.post<{ avatar_url: string }>('/users/me/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }

  /**
   * Clear user cache
   */
  clearCache(): void {
    this.userCache.clear()
  }

  /**
   * Get current user role for permission checks
   */
  getCurrentUserRole(): User['role'] | null {
    return this.currentUser?.role || null
  }

  /**
   * Check if current user has admin privileges
   */
  isAdmin(): boolean {
    return this.currentUser?.role === 'admin'
  }

  /**
   * Check if current user has moderator or admin privileges
   */
  isModerator(): boolean {
    return this.currentUser?.role === 'moderator' || this.currentUser?.role === 'admin'
  }
}

// Export singleton instance
export const usersApiClient = new UsersApiClient()
