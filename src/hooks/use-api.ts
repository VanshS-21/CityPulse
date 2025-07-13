/**
 * Enhanced API Hooks with React 19 Integration
 * Modern data fetching with concurrent features and optimistic updates
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions,
} from '@tanstack/react-query'
import { startTransition } from 'react'
import { queryKeys, optimisticUpdates } from '@/lib/react-query'
import { apiClient } from '@/services/api/client'
import { useAppStore } from '@/store/app-store'
import { logger } from '@/lib/logger'
import { config } from '@/lib/config'

// Types
interface ApiError {
  message: string
  code?: string
  statusCode?: number
}

interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  hasMore: boolean
}

// React 19 optimized performance tracking
function usePerformanceTracking() {
  const { addPerformanceMetric } = useAppStore()

  return {
    trackApiCall: (endpoint: string, startTime: number) => {
      const duration = performance.now() - startTime
      startTransition(() => {
        addPerformanceMetric?.('api_response_times', duration)
      })
    },
  }
}

// Events API Hooks with React 19 patterns
export function useEvents(
  filters?: any,
  options?: Omit<UseQueryOptions<any, ApiError>, 'queryKey' | 'queryFn'>
) {
  const { trackApiCall } = usePerformanceTracking()

  return useQuery({
    queryKey: queryKeys.events.list(filters || {}),
    queryFn: async () => {
      const startTime = performance.now()
      try {
        const result = await apiClient.get('/api/v1/events', {
          params: filters,
        })
        trackApiCall('events_list', startTime)
        return result
      } catch (error) {
        trackApiCall('events_list', startTime)
        throw error
      }
    },
    staleTime: config.cache.defaultTTL,
    ...options,
  })
}

export function useEvent(
  id: string,
  options?: Omit<UseQueryOptions<any, ApiError>, 'queryKey' | 'queryFn'>
) {
  const { trackApiCall } = usePerformanceTracking()

  return useQuery({
    queryKey: queryKeys.events.detail(id),
    queryFn: async () => {
      const startTime = performance.now()
      try {
        const result = await apiClient.get(`/api/v1/events/${id}`)
        trackApiCall('events_detail', startTime)
        return result
      } catch (error) {
        trackApiCall('events_detail', startTime)
        throw error
      }
    },
    enabled: !!id,
    staleTime: config.cache.longTTL,
    ...options,
  })
}

export function useNearbyEvents(
  latitude: number,
  longitude: number,
  radius: number = 10,
  options?: Omit<UseQueryOptions<any, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.events.nearby(latitude, longitude, radius),
    queryFn: async () => {
      const result = await apiClient.get('/api/v1/events/nearby', {
        params: { latitude, longitude, radius },
      })
      return result
    },
    enabled: !!(latitude && longitude),
    staleTime: config.cache.shortTTL,
    ...options,
  })
}

// React 19 optimized mutations with concurrent features
export function useCreateEvent(
  options?: UseMutationOptions<any, ApiError, any>
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (eventData: any) => {
      const result = await apiClient.post('/api/v1/events', eventData)
      return result
    },
    onMutate: async (newEvent: any): Promise<{ tempId: string; optimisticEvent: any }> => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.events.all })

      const tempId = `temp_${Date.now()}`
      const optimisticEvent = {
        ...newEvent,
        id: tempId,
        createdAt: new Date().toISOString(),
      }

      // Optimistically update cache
      queryClient.setQueryData(queryKeys.events.lists(), (old: any) => {
        if (!old) return { events: [optimisticEvent], total: 1 }
        return {
          ...old,
          events: [optimisticEvent, ...old.events],
          total: old.total + 1,
        }
      })

      return { tempId, optimisticEvent }
    },
    onSuccess: (data, variables, context) => {
      startTransition(() => {
        queryClient.invalidateQueries({ queryKey: queryKeys.events.all })
        logger.info('Event created successfully', { eventId: data.id })
      })
    },
    onError: (error, variables, context) => {
      startTransition(() => {
        queryClient.invalidateQueries({ queryKey: queryKeys.events.all })
        logger.error('Failed to create event', error as Error)
      })
    },
    ...options,
  })
}

export function useUpdateEvent(
  options?: UseMutationOptions<any, ApiError, { id: string; updates: any }>
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, updates }) => {
      const result = await apiClient.put(`/api/v1/events/${id}`, updates)
      return result
    },
    onMutate: async ({ id, updates }) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.events.detail(id) })

      queryClient.setQueryData(queryKeys.events.detail(id), (old: any) => ({
        ...old,
        ...updates,
      }))

      return { id, updates }
    },
    onSuccess: (data, { id }) => {
      startTransition(() => {
        queryClient.invalidateQueries({ queryKey: queryKeys.events.detail(id) })
        logger.info('Event updated successfully', { eventId: id })
      })
    },
    onError: (error, { id }) => {
      startTransition(() => {
        queryClient.invalidateQueries({ queryKey: queryKeys.events.detail(id) })
        logger.error('Failed to update event', error as Error, { eventId: id })
      })
    },
    ...options,
  })
}

// Users API Hooks with React 19 patterns
export function useCurrentUser(
  options?: Omit<UseQueryOptions<any, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.users.profile(),
    queryFn: async () => {
      const result = await apiClient.get('/api/v1/users/me')
      return result
    },
    staleTime: config.cache.longTTL,
    retry: false,
    ...options,
  })
}

export function useUpdateProfile(
  options?: UseMutationOptions<any, ApiError, any>
) {
  const queryClient = useQueryClient()
  const { setUser } = useAppStore()

  return useMutation({
    mutationFn: async (updates: any) => {
      const result = await apiClient.put('/api/v1/users/me', updates)
      return result
    },
    onSuccess: data => {
      startTransition(() => {
        queryClient.setQueryData(queryKeys.users.profile(), data)
        setUser?.(data)
        logger.info('Profile updated successfully')
      })
    },
    onError: error => {
      startTransition(() => {
        logger.error('Failed to update profile', error as Error)
      })
    },
    ...options,
  })
}

// Analytics API Hooks
export function useDashboardMetrics(
  filters?: any,
  options?: Omit<UseQueryOptions<any, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.analytics.dashboard(),
    queryFn: async () => {
      const result = await apiClient.get('/api/v1/analytics/dashboard', {
        params: filters,
      })
      return result
    },
    staleTime: config.cache.defaultTTL,
    ...options,
  })
}

// React 19 optimized cache management
export function useCacheManager() {
  const queryClient = useQueryClient()

  return {
    invalidateEvents: () => {
      startTransition(() => {
        queryClient.invalidateQueries({ queryKey: queryKeys.events.all })
      })
    },
    invalidateUsers: () => {
      startTransition(() => {
        queryClient.invalidateQueries({ queryKey: queryKeys.users.all })
      })
    },
    invalidateAll: () => {
      startTransition(() => {
        queryClient.invalidateQueries()
      })
    },
    clearCache: () => {
      startTransition(() => {
        queryClient.clear()
      })
    },
    getCacheData: (queryKey: any) => queryClient.getQueryData(queryKey),
    setCacheData: (queryKey: any, data: any) => {
      startTransition(() => {
        queryClient.setQueryData(queryKey, data)
      })
    },
  }
}

// React 19 performance monitoring hook
export function useApiPerformance() {
  const { performanceMetrics } = useAppStore()

  return {
    metrics: performanceMetrics,
    getAverageResponseTime: (endpoint: string) => {
      const times = performanceMetrics.apiResponseTimes[endpoint] || []
      return times.length > 0
        ? times.reduce((a, b) => a + b, 0) / times.length
        : 0
    },
    getSlowEndpoints: (threshold = 1000) => {
      return Object.entries(performanceMetrics.apiResponseTimes)
        .filter(([, times]) => {
          const avg = times.reduce((a, b) => a + b, 0) / times.length
          return avg > threshold
        })
        .map(([endpoint]) => endpoint)
    },
  }
}
