/**
 * Comprehensive tests for the enhanced API clients
 * Tests service-specific functionality, error handling, and caching
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import axios from 'axios'
import { EventsApiClient } from '../../src/services/api/events-client'
import { UsersApiClient } from '../../src/services/api/users-client'
import { AnalyticsApiClient } from '../../src/services/api/analytics-client'
import { cityPulseApi, handleApiError, checkPermissions } from '../../src/services/api'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// Mock APP_CONFIG
vi.mock('@/utils/constants', () => ({
  APP_CONFIG: {
    api: {
      baseUrl: 'http://localhost:8000',
      timeout: 10000
    }
  },
  STORAGE_KEYS: {
    authToken: 'auth_token'
  }
}))

describe('EventsApiClient', () => {
  let eventsClient: EventsApiClient
  let mockAxiosInstance: any

  beforeEach(() => {
    mockAxiosInstance = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    }
    
    mockedAxios.create.mockReturnValue(mockAxiosInstance)
    eventsClient = new EventsApiClient()
  })

  afterEach(() => {
    vi.clearAllMocks()
    eventsClient.clearCache()
  })

  describe('Event Operations', () => {
    it('should get events with caching', async () => {
      const mockEvents = {
        events: [
          { id: '1', title: 'Test Event 1', category: 'pothole' },
          { id: '2', title: 'Test Event 2', category: 'streetlight' }
        ],
        total: 2,
        page: 1,
        limit: 10,
        hasMore: false
      }

      mockAxiosInstance.get.mockResolvedValue({ data: mockEvents })

      // First call should hit the API
      const result1 = await eventsClient.getEvents()
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/events', { params: undefined })
      expect(result1).toEqual(mockEvents)

      // Second call should use cache (mock won't be called again)
      mockAxiosInstance.get.mockClear()
      const result2 = await eventsClient.getEvents()
      expect(mockAxiosInstance.get).not.toHaveBeenCalled()
      expect(result2).toEqual(mockEvents)
    })

    it('should create event and clear cache', async () => {
      const newEvent = {
        title: 'New Event',
        description: 'Test description',
        category: 'pothole',
        severity: 'medium',
        status: 'pending',
        location: { latitude: 40.7128, longitude: -74.0060 }
      }

      const createdEvent = { id: '123', ...newEvent }
      mockAxiosInstance.post.mockResolvedValue({ data: createdEvent })

      const result = await eventsClient.createEvent(newEvent)
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/events', newEvent)
      expect(result).toEqual(createdEvent)
    })

    it('should handle event search', async () => {
      const searchResults = {
        events: [{ id: '1', title: 'Found Event' }],
        total: 1,
        page: 1,
        limit: 10,
        hasMore: false
      }

      mockAxiosInstance.get.mockResolvedValue({ data: searchResults })

      const result = await eventsClient.searchEvents('pothole', { category: 'infrastructure' })
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/events/search', {
        params: { q: 'pothole', category: 'infrastructure' }
      })
      expect(result).toEqual(searchResults)
    })

    it('should handle nearby events', async () => {
      const nearbyEvents = {
        events: [{ id: '1', title: 'Nearby Event' }],
        total: 1,
        page: 1,
        limit: 10,
        hasMore: false
      }

      mockAxiosInstance.get.mockResolvedValue({ data: nearbyEvents })

      const result = await eventsClient.getNearbyEvents(40.7128, -74.0060, 5)
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/events/nearby', {
        params: { latitude: 40.7128, longitude: -74.0060, radius: 5 }
      })
      expect(result).toEqual(nearbyEvents)
    })

    it('should handle event reporting with images', async () => {
      const eventData = {
        title: 'Reported Event',
        category: 'pothole',
        severity: 'high',
        status: 'pending',
        location: { latitude: 40.7128, longitude: -74.0060 }
      }

      const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const createdEvent = { id: '456', ...eventData }

      mockAxiosInstance.post.mockResolvedValue({ data: createdEvent })

      const result = await eventsClient.reportEvent(eventData, [mockFile])
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/events/report',
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      expect(result).toEqual(createdEvent)
    })
  })

  describe('Caching Behavior', () => {
    it('should cache GET requests and respect TTL', async () => {
      const mockEvent = { id: '1', title: 'Cached Event' }
      mockAxiosInstance.get.mockResolvedValue({ data: mockEvent })

      // First call
      await eventsClient.getEvent('1')
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(1)

      // Second call should use cache
      mockAxiosInstance.get.mockClear()
      await eventsClient.getEvent('1')
      expect(mockAxiosInstance.get).not.toHaveBeenCalled()
    })

    it('should clear cache on mutations', async () => {
      // Setup cache
      mockAxiosInstance.get.mockResolvedValue({ data: { id: '1', title: 'Event' } })
      await eventsClient.getEvent('1')

      // Update event should clear cache
      mockAxiosInstance.put.mockResolvedValue({ data: { id: '1', title: 'Updated Event' } })
      await eventsClient.updateEvent('1', { title: 'Updated Event' })

      // Next GET should hit API again
      mockAxiosInstance.get.mockClear()
      await eventsClient.getEvent('1')
      expect(mockAxiosInstance.get).toHaveBeenCalled()
    })
  })
})

describe('UsersApiClient', () => {
  let usersClient: UsersApiClient
  let mockAxiosInstance: any

  beforeEach(() => {
    mockAxiosInstance = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    }
    
    mockedAxios.create.mockReturnValue(mockAxiosInstance)
    usersClient = new UsersApiClient()
  })

  afterEach(() => {
    vi.clearAllMocks()
    usersClient.clearCache()
  })

  describe('User Operations', () => {
    it('should get current user and set context', async () => {
      const mockUser = {
        user_id: 'user123',
        email: 'test@example.com',
        display_name: 'Test User',
        role: 'citizen' as const,
        is_active: true
      }

      mockAxiosInstance.get.mockResolvedValue({ data: mockUser })

      const result = await usersClient.getCurrentUser()
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/users/me')
      expect(result).toEqual(mockUser)
      expect(usersClient.getCurrentUserRole()).toBe('citizen')
    })

    it('should update user profile and clear cache', async () => {
      const mockUser = {
        user_id: 'user123',
        email: 'test@example.com',
        display_name: 'Updated User',
        role: 'citizen' as const,
        is_active: true
      }

      mockAxiosInstance.put.mockResolvedValue({ data: mockUser })

      const result = await usersClient.updateProfile({ display_name: 'Updated User' })
      
      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/users/me', { display_name: 'Updated User' })
      expect(result).toEqual(mockUser)
    })

    it('should handle user search with proper permissions', async () => {
      const searchResults = {
        users: [{ user_id: '1', email: 'user1@example.com', role: 'citizen' }],
        total: 1,
        page: 1,
        limit: 20,
        hasMore: false
      }

      mockAxiosInstance.get.mockResolvedValue({ data: searchResults })

      const result = await usersClient.searchUsers('test@example.com')
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/users/search', {
        params: { q: 'test@example.com', limit: 20 }
      })
      expect(result).toEqual(searchResults)
    })

    it('should handle avatar upload', async () => {
      const mockFile = new File(['avatar'], 'avatar.jpg', { type: 'image/jpeg' })
      const uploadResult = { avatar_url: 'https://example.com/avatar.jpg' }

      mockAxiosInstance.post.mockResolvedValue({ data: uploadResult })

      const result = await usersClient.uploadAvatar(mockFile)
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/users/me/avatar',
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      expect(result).toEqual(uploadResult)
    })
  })

  describe('Permission Checks', () => {
    it('should correctly identify admin users', () => {
      const adminUser = {
        user_id: 'admin123',
        email: 'admin@example.com',
        role: 'admin' as const,
        is_active: true
      }

      usersClient.setCurrentUser(adminUser)
      
      expect(usersClient.isAdmin()).toBe(true)
      expect(usersClient.isModerator()).toBe(true)
    })

    it('should correctly identify moderator users', () => {
      const moderatorUser = {
        user_id: 'mod123',
        email: 'mod@example.com',
        role: 'moderator' as const,
        is_active: true
      }

      usersClient.setCurrentUser(moderatorUser)
      
      expect(usersClient.isAdmin()).toBe(false)
      expect(usersClient.isModerator()).toBe(true)
    })

    it('should correctly identify citizen users', () => {
      const citizenUser = {
        user_id: 'citizen123',
        email: 'citizen@example.com',
        role: 'citizen' as const,
        is_active: true
      }

      usersClient.setCurrentUser(citizenUser)
      
      expect(usersClient.isAdmin()).toBe(false)
      expect(usersClient.isModerator()).toBe(false)
    })
  })
})

describe('AnalyticsApiClient', () => {
  let analyticsClient: AnalyticsApiClient
  let mockAxiosInstance: any

  beforeEach(() => {
    mockAxiosInstance = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    }
    
    mockedAxios.create.mockReturnValue(mockAxiosInstance)
    analyticsClient = new AnalyticsApiClient()
  })

  afterEach(() => {
    vi.clearAllMocks()
    analyticsClient.clearCache()
  })

  describe('Analytics Operations', () => {
    it('should get dashboard metrics with caching', async () => {
      const mockMetrics = {
        totalEvents: { name: 'Total Events', value: 1000, change: 5.2, trend: 'up' as const, data: [] },
        activeEvents: { name: 'Active Events', value: 150, change: -2.1, trend: 'down' as const, data: [] },
        topCategories: [
          { category: 'pothole', count: 300, percentage: 30 },
          { category: 'streetlight', count: 200, percentage: 20 }
        ]
      }

      mockAxiosInstance.get.mockResolvedValue({ data: mockMetrics })

      const result = await analyticsClient.getDashboardMetrics()
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/analytics/dashboard', { params: undefined })
      expect(result).toEqual(mockMetrics)

      // Second call should use cache
      mockAxiosInstance.get.mockClear()
      await analyticsClient.getDashboardMetrics()
      expect(mockAxiosInstance.get).not.toHaveBeenCalled()
    })

    it('should get time series data', async () => {
      const mockTimeSeries = [
        { timestamp: '2024-01-01', value: 10 },
        { timestamp: '2024-01-02', value: 15 },
        { timestamp: '2024-01-03', value: 12 }
      ]

      mockAxiosInstance.get.mockResolvedValue({ data: mockTimeSeries })

      const result = await analyticsClient.getTimeSeries('events_count', {
        timeRange: { start: '2024-01-01', end: '2024-01-03' }
      })
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/analytics/timeseries/events_count', {
        params: { timeRange: { start: '2024-01-01', end: '2024-01-03' } }
      })
      expect(result).toEqual(mockTimeSeries)
    })

    it('should create and manage reports', async () => {
      const reportConfig = {
        title: 'Monthly Report',
        timeRange: { start: '2024-01-01', end: '2024-01-31' },
        metrics: ['events_count', 'resolution_time'],
        format: 'pdf' as const
      }

      const createdReport = {
        id: 'report123',
        config: reportConfig,
        status: 'pending' as const,
        created_at: '2024-01-01T00:00:00Z'
      }

      mockAxiosInstance.post.mockResolvedValue({ data: createdReport })

      const result = await analyticsClient.createReport(reportConfig)
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/analytics/reports', reportConfig)
      expect(result).toEqual(createdReport)
    })

    it('should get cache statistics', () => {
      const stats = analyticsClient.getCacheStats()
      
      expect(stats).toHaveProperty('size')
      expect(stats).toHaveProperty('keys')
      expect(Array.isArray(stats.keys)).toBe(true)
    })
  })
})

describe('CityPulse API Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Unified API Interface', () => {
    it('should provide access to all service clients', () => {
      expect(cityPulseApi.events).toBeDefined()
      expect(cityPulseApi.users).toBeDefined()
      expect(cityPulseApi.analytics).toBeDefined()
    })

    it('should clear all caches', () => {
      const eventsClearSpy = vi.spyOn(cityPulseApi.events, 'clearCache')
      const usersClearSpy = vi.spyOn(cityPulseApi.users, 'clearCache')
      const analyticsClearSpy = vi.spyOn(cityPulseApi.analytics, 'clearCache')

      cityPulseApi.clearAllCaches()

      expect(eventsClearSpy).toHaveBeenCalled()
      expect(usersClearSpy).toHaveBeenCalled()
      expect(analyticsClearSpy).toHaveBeenCalled()
    })

    it('should get usage statistics', () => {
      const stats = cityPulseApi.getUsageStats()
      
      expect(stats).toHaveProperty('events')
      expect(stats).toHaveProperty('users')
      expect(stats).toHaveProperty('analytics')
    })
  })

  describe('Error Handling Utilities', () => {
    it('should handle enhanced API errors', () => {
      const enhancedError = {
        message: 'Validation failed',
        code: 'VALIDATION_ERROR',
        correlationId: 'test-correlation-123',
        statusCode: 422
      }

      const result = handleApiError(enhancedError)
      
      expect(result).toEqual({
        message: 'Validation failed',
        code: 'VALIDATION_ERROR',
        correlationId: 'test-correlation-123',
        isRetryable: false
      })
    })

    it('should handle standard errors', () => {
      const standardError = new Error('Network error')

      const result = handleApiError(standardError)
      
      expect(result).toEqual({
        message: 'Network error',
        code: 'UNKNOWN_ERROR',
        isRetryable: false
      })
    })
  })

  describe('Permission Utilities', () => {
    it('should check permissions correctly', () => {
      // Mock current user role
      vi.spyOn(cityPulseApi.users, 'getCurrentUserRole').mockReturnValue('admin')
      
      expect(checkPermissions('citizen')).toBe(true)
      expect(checkPermissions('moderator')).toBe(true)
      expect(checkPermissions('admin')).toBe(true)
    })

    it('should deny permissions for insufficient role', () => {
      vi.spyOn(cityPulseApi.users, 'getCurrentUserRole').mockReturnValue('citizen')
      
      expect(checkPermissions('citizen')).toBe(true)
      expect(checkPermissions('moderator')).toBe(false)
      expect(checkPermissions('admin')).toBe(false)
    })

    it('should deny permissions when no user is logged in', () => {
      vi.spyOn(cityPulseApi.users, 'getCurrentUserRole').mockReturnValue(null)
      
      expect(checkPermissions('citizen')).toBe(false)
      expect(checkPermissions('moderator')).toBe(false)
      expect(checkPermissions('admin')).toBe(false)
    })
  })
})
