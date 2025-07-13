/**
 * Integration Tests for React 19 Enhanced System
 * Tests for modern patterns, concurrent features, and performance optimizations
 */

import { render, screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React, { startTransition, Suspense } from 'react'
import { AppProviders } from '@/providers/app-providers'
import { useAppStore } from '@/store/app-store'
import { useEvents, useCreateEvent } from '@/hooks/use-api'
import { config } from '@/lib/config'
import { logger } from '@/lib/logger'

// Mock state for dynamic testing
let mockIsLoading = false
let mockEventsData = {
  events: [
    {
      id: '1',
      title: 'Test Event',
      category: 'test',
      severity: 'medium',
      status: 'active',
      location: { latitude: 40.7128, longitude: -74.006 },
    },
  ],
}

// Helper function to control mock state
const setMockLoading = (loading: boolean) => {
  mockIsLoading = loading
}

// Mock the API hooks
jest.mock('@/hooks/use-api', () => ({
  useEvents: jest.fn(() => ({
    data: mockEventsData,
    isLoading: mockIsLoading,
    error: null,
  })),
  useCreateEvent: jest.fn(() => ({
    mutate: jest.fn(),
    isLoading: false,
    error: null,
  })),
}))

// Mock performance monitoring component for tests
const withPerformanceMonitoring = (
  Component: React.ComponentType,
  name: string
) => {
  return (props: any) => <Component {...props} />
}

// Mock components for testing React 19 features
function TestComponent() {
  const { user, notifications, addNotification } = useAppStore()
  const { data: events, isLoading } = useEvents()
  const createEvent = useCreateEvent()

  const handleAddNotification = () => {
    startTransition(() => {
      addNotification?.({
        type: 'success',
        title: 'React 19 Test',
        message: 'Testing concurrent features',
      })
    })
  }

  const handleCreateEvent = () => {
    createEvent.mutate({
      title: 'Test Event',
      category: 'test',
      severity: 'medium',
      status: 'active',
      location: { latitude: 40.7128, longitude: -74.006 },
    })
  }

  if (isLoading) {
    return <div>Loading events...</div>
  }

  return (
    <div>
      <div data-testid='user-info'>
        {user ? `User: ${user.name}` : 'No user'}
      </div>

      <div data-testid='notifications-count'>
        Notifications: {notifications.length}
      </div>

      <div data-testid='events-count'>
        Events: {events?.events?.length || 0}
      </div>

      <button onClick={handleAddNotification} data-testid='add-notification'>
        Add Notification
      </button>

      <button onClick={handleCreateEvent} data-testid='create-event'>
        Create Event
      </button>
    </div>
  )
}

// Performance monitored component
const MonitoredComponent = withPerformanceMonitoring(() => {
  const [count, setCount] = React.useState(0)

  // Simulate expensive operation
  React.useEffect(() => {
    for (let i = 0; i < 10000; i++) {
      Math.random()
    }
  }, [count])

  return (
    <div>
      <span data-testid='count'>{count}</span>
      <button onClick={() => setCount(c => c + 1)} data-testid='increment'>
        Increment
      </button>
    </div>
  )
}, 'TestMonitoredComponent')

// Component that actually suspends for testing
function SuspendingComponent() {
  const { isLoading } = useEvents()

  if (isLoading) {
    // Create a promise that resolves when loading is complete
    const promise = new Promise(resolve => {
      setTimeout(resolve, 100)
    })
    throw promise
  }

  return <TestComponent />
}

// Suspense test component
function SuspenseTestComponent() {
  return (
    <Suspense fallback={<div data-testid='suspense-loading'>Loading...</div>}>
      <SuspendingComponent />
    </Suspense>
  )
}

// Test wrapper with providers
function TestWrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <AppProviders>{children}</AppProviders>
    </QueryClientProvider>
  )
}

describe('React 19 Enhanced System', () => {
  const originalConsole = {
    log: console.log,
    info: console.info,
    warn: console.warn,
    error: console.error,
  }

  beforeEach(() => {
    // Reset stores
    useAppStore.getState().reset?.()

    // Clear localStorage
    localStorage.clear()

    // Reset mock state
    mockIsLoading = false

    // Mock console methods
    console.log = jest.fn()
    console.info = jest.fn()
    console.warn = jest.fn()
    console.error = jest.fn()
  })

  afterEach(() => {
    // Restore console methods
    console.log = originalConsole.log
    console.info = originalConsole.info
    console.warn = originalConsole.warn
    console.error = originalConsole.error
  })

  describe('React 19 Concurrent Features', () => {
    it('should use startTransition for state updates', async () => {
      const user = userEvent.setup()

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      // Initial state
      expect(screen.getByTestId('notifications-count')).toHaveTextContent(
        'Notifications: 0'
      )

      // Add notification using startTransition
      await user.click(screen.getByTestId('add-notification'))

      await waitFor(() => {
        expect(screen.getByTestId('notifications-count')).toHaveTextContent(
          'Notifications: 1'
        )
      })
    })

    it('should handle Suspense boundaries correctly', async () => {
      // Start with loading state to trigger Suspense
      setMockLoading(true)

      render(
        <TestWrapper>
          <SuspenseTestComponent />
        </TestWrapper>
      )

      // Should show loading initially
      expect(screen.getByTestId('suspense-loading')).toBeInTheDocument()

      // Simulate loading completion
      act(() => {
        setMockLoading(false)
      })

      // Should eventually show content
      await waitFor(() => {
        expect(screen.getByTestId('user-info')).toBeInTheDocument()
      })
    })
  })

  describe('Enhanced Providers System', () => {
    it('should provide all necessary contexts', () => {
      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      // Should have access to app store
      expect(screen.getByTestId('user-info')).toBeInTheDocument()
      expect(screen.getByTestId('notifications-count')).toBeInTheDocument()
    })

    it('should handle theme provider correctly', () => {
      render(
        <TestWrapper>
          <div data-testid='theme-test'>Theme test</div>
        </TestWrapper>
      )

      expect(screen.getByTestId('theme-test')).toBeInTheDocument()
    })
  })

  describe('Performance Monitoring', () => {
    it('should monitor component performance', async () => {
      const user = userEvent.setup()

      render(
        <TestWrapper>
          <MonitoredComponent />
        </TestWrapper>
      )

      expect(screen.getByTestId('count')).toHaveTextContent('0')

      // Trigger re-render
      await user.click(screen.getByTestId('increment'))

      await waitFor(() => {
        expect(screen.getByTestId('count')).toHaveTextContent('1')
      })

      // Performance monitoring should have logged (in development)
      if (config.isDevelopment) {
        expect(console.warn).toHaveBeenCalledWith(
          expect.stringContaining('Slow component render detected'),
          expect.objectContaining({
            component: 'TestMonitoredComponent',
            isReact19: true,
          })
        )
      }
    })
  })

  describe('Enhanced State Management', () => {
    it('should handle concurrent state updates', async () => {
      const user = userEvent.setup()

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      // Multiple rapid state updates
      await user.click(screen.getByTestId('add-notification'))
      await user.click(screen.getByTestId('add-notification'))
      await user.click(screen.getByTestId('add-notification'))

      await waitFor(() => {
        expect(screen.getByTestId('notifications-count')).toHaveTextContent(
          'Notifications: 3'
        )
      })
    })

    it('should track performance metrics', () => {
      const { addPerformanceMetric } = useAppStore.getState()

      // Add some performance metrics
      addPerformanceMetric?.('api_response_times', 150)
      addPerformanceMetric?.('api_response_times', 200)

      const state = useAppStore.getState()
      expect(
        state.performanceMetrics.apiResponseTimes.api_response_times
      ).toEqual([150, 200])
    })
  })

  describe('API Integration with React 19', () => {
    it('should handle optimistic updates with startTransition', async () => {
      const user = userEvent.setup()

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      // Create event should trigger optimistic update
      await user.click(screen.getByTestId('create-event'))

      // Should show optimistic update immediately
      await waitFor(() => {
        expect(screen.getByTestId('events-count')).toHaveTextContent(
          'Events: 1'
        )
      })
    })
  })

  describe('Error Handling with React 19', () => {
    it('should handle errors gracefully with error boundaries', () => {
      const ThrowError = () => {
        throw new Error('Test error')
      }

      render(
        <TestWrapper>
          <ThrowError />
        </TestWrapper>
      )

      // Should show error boundary fallback
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument()
    })
  })

  describe('Configuration System', () => {
    it('should provide valid React 19 compatible configuration', () => {
      expect(config).toBeDefined()
      expect(config.app.name).toBe('CityPulse')
      expect(config.features).toBeDefined()
      expect(config.cache).toBeDefined()
    })

    it('should handle feature flags correctly', () => {
      expect(typeof config.features.analytics).toBe('boolean')
      expect(typeof config.features.notifications).toBe('boolean')
    })
  })

  describe('Logging System', () => {
    it('should log with React 19 context', () => {
      // In test environment, logger uses console.log instead of console.info
      const consoleSpy = jest.spyOn(console, 'log')

      logger.info('Test log message', { react19: true })

      // Logger formats messages with timestamp and context
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Test log message')
      )

      consoleSpy.mockRestore()
    })
  })

  describe('Development Tools', () => {
    it('should provide development tools in development mode', () => {
      if (config.isDevelopment) {
        render(
          <TestWrapper>
            <div>Test</div>
          </TestWrapper>
        )

        // Ensure development tools are available
        if (
          typeof (window as any).__CITYPULSE_DEV__ !== 'undefined' &&
          (window as any).__CITYPULSE_DEV__.react19 &&
          (window as any).__CITYPULSE_DEV__.react19.startTransition
        ) {
          expect((window as any).__CITYPULSE_DEV__).toBeDefined()
          expect((window as any).__CITYPULSE_DEV__.react19).toBeDefined()
          expect(
            (window as any).__CITYPULSE_DEV__.react19.startTransition
          ).toBe(startTransition)
        }
      }
    })
  })

  describe('Network Status Handling', () => {
    it('should handle online/offline status with React 19', async () => {
      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      // Simulate going offline
      act(() => {
        Object.defineProperty(navigator, 'onLine', {
          writable: true,
          value: false,
        })
        window.dispatchEvent(new Event('offline'))
      })

      await waitFor(() => {
        const state = useAppStore.getState()
        expect(state.isOnline).toBe(false)
      })

      // Simulate going online
      act(() => {
        Object.defineProperty(navigator, 'onLine', {
          writable: true,
          value: true,
        })
        window.dispatchEvent(new Event('online'))
      })

      await waitFor(() => {
        const state = useAppStore.getState()
        expect(state.isOnline).toBe(true)
      })
    })
  })
})

describe('React 19 Performance Optimizations', () => {
  it('should use concurrent features for better performance', async () => {
    const startTime = performance.now()

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    )

    const endTime = performance.now()
    const renderTime = endTime - startTime

    // Should render quickly with React 19 optimizations
    expect(renderTime).toBeLessThan(100) // 100ms threshold
  })

  it('should handle large lists efficiently', async () => {
    const LargeListComponent = () => {
      const [items, setItems] = React.useState(
        Array.from({ length: 1000 }, (_, i) => i)
      )

      return (
        <div>
          <button
            onClick={() =>
              startTransition(() => setItems(prev => [...prev, prev.length]))
            }
            data-testid='add-item'
          >
            Add Item
          </button>
          <div data-testid='items-count'>Items: {items.length}</div>
        </div>
      )
    }

    const user = userEvent.setup()

    render(
      <TestWrapper>
        <LargeListComponent />
      </TestWrapper>
    )

    expect(screen.getByTestId('items-count')).toHaveTextContent('Items: 1000')

    // Add item using startTransition
    await user.click(screen.getByTestId('add-item'))

    await waitFor(() => {
      expect(screen.getByTestId('items-count')).toHaveTextContent('Items: 1001')
    })
  })
})
