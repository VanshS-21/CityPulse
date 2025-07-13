/**
 * Enhanced Application Providers
 * React 19 optimized provider setup with modern patterns and performance optimization
 */

'use client'

import React, { ReactNode, useEffect, Suspense, startTransition, use } from 'react'
import { ThemeProvider } from 'next-themes'
import { Toaster } from '@/components/ui/sonner'
import { ErrorBoundary } from '@/lib/error-handling'
import { QueryProvider } from '@/lib/react-query'
import { config } from '@/lib/config'
import { logger } from '@/lib/logger'
import { useAppStore } from '@/store/app-store'

// React 19 Performance Provider
function PerformanceProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    // Use React 19 scheduler for performance monitoring
    startTransition(() => {
      if (typeof window !== 'undefined' && window.performance && window.performance.timing) {
        const timing = window.performance.timing
        const loadTime = timing.loadEventEnd && timing.navigationStart
          ? timing.loadEventEnd - timing.navigationStart
          : 0
        
        if (loadTime > 0) {
          const { addPerformanceMetric } = useAppStore.getState()
          addPerformanceMetric?.('page_load', loadTime)
          
          logger.info('Page load performance', {
            loadTime,
            domContentLoaded: window.performance.timing.domContentLoadedEventEnd - window.performance.timing.navigationStart,
          })
        }
      }
    })
  }, [])

  return <>{children}</>
}

// Enhanced Network Status Provider with React 19 patterns
function NetworkStatusProvider({ children }: { children: ReactNode }) {
  const setOnlineStatus = useAppStore((state) => state.setOnlineStatus)

  useEffect(() => {
    const handleOnline = () => {
      startTransition(() => {
        setOnlineStatus?.(true)
        logger.info('Network connection restored')
      })
    }

    const handleOffline = () => {
      startTransition(() => {
        setOnlineStatus?.(false)
        logger.warn('Network connection lost')
      })
    }

    // Set initial status
    setOnlineStatus?.(navigator.onLine)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [setOnlineStatus])

  return <>{children}</>
}

// React 19 optimized notification provider
function NotificationProvider({ children }: { children: ReactNode }) {
  const notifications = useAppStore((state) => state.notifications)
  const removeNotification = useAppStore((state) => state.removeNotification)

  useEffect(() => {
    // Use React 19 concurrent features for notification management
    notifications.forEach((notification) => {
      if (!notification.persistent && notification.duration) {
        const timeRemaining = notification.duration - (Date.now() - notification.timestamp)
        
        if (timeRemaining > 0) {
          setTimeout(() => {
            startTransition(() => {
              removeNotification?.(notification.id)
            })
          }, timeRemaining)
        } else {
          startTransition(() => {
            removeNotification?.(notification.id)
          })
        }
      }
    })
  }, [notifications, removeNotification])

  return (
    <>
      {children}
      <Toaster
        position="top-right"
        expand={true}
        richColors
        closeButton
        toastOptions={{
          duration: config.notifications.defaultDuration,
          className: 'toast',
        }}
      />
    </>
  )
}

// Error tracking with React 19 error handling
function ErrorTrackingProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      startTransition(() => {
        logger.error('Global error caught', new Error(event.message), {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          stack: event.error?.stack,
        })
      })
    }

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      startTransition(() => {
        logger.error('Unhandled promise rejection', new Error(String(event.reason)), {
          reason: event.reason,
        })
      })
    }

    window.addEventListener('error', handleError)
    window.addEventListener('unhandledrejection', handleUnhandledRejection)

    return () => {
      window.removeEventListener('error', handleError)
      window.removeEventListener('unhandledrejection', handleUnhandledRejection)
    }
  }, [])

  return <>{children}</>
}

// Development tools with React 19 features
function DevToolsProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    if (config.isDevelopment) {
      startTransition(() => {
        // Add development helpers to window
        (window as any).__CITYPULSE_DEV__ = {
          config,
          logger,
          stores: {
            app: useAppStore,
          },
          react19: {
            startTransition,
            use,
          },
          clearAllCaches: () => {
            localStorage.clear()
            sessionStorage.clear()
            if ('caches' in window) {
              caches.keys().then(names => {
                names.forEach(name => caches.delete(name))
              })
            }
          },
        }

        logger.info('Development tools available at window.__CITYPULSE_DEV__')
      })
    }
  }, [])

  return <>{children}</>
}

// React 19 Suspense wrapper with enhanced loading
function SuspenseWrapper({ children }: { children: ReactNode }) {
  return (
    <Suspense 
      fallback={
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      }
    >
      {children}
    </Suspense>
  )
}

// Main app providers with React 19 optimizations
interface AppProvidersProps {
  children: ReactNode
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <ErrorBoundary>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem={true}
        disableTransitionOnChange={false}
      >
        <QueryProvider>
          <SuspenseWrapper>
            <PerformanceProvider>
              <NetworkStatusProvider>
                <ErrorTrackingProvider>
                  <NotificationProvider>
                    <DevToolsProvider>
                      <ErrorBoundary>
                        {children}
                      </ErrorBoundary>
                    </DevToolsProvider>
                  </NotificationProvider>
                </ErrorTrackingProvider>
              </NetworkStatusProvider>
            </PerformanceProvider>
          </SuspenseWrapper>
        </QueryProvider>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

// Feature provider with React 19 patterns
export function FeatureProvider({ 
  children, 
  feature 
}: { 
  children: ReactNode
  feature: keyof typeof config.features 
}) {
  if (!config.features[feature]) {
    return null
  }

  return <Suspense fallback={<div>Loading feature...</div>}>{children}</Suspense>
}

// HOC for feature gating with React 19
export function withFeatureGate<P extends object>(
  Component: React.ComponentType<P>,
  feature: keyof typeof config.features,
  fallback?: ReactNode
) {
  return function FeatureGatedComponent(props: P) {
    if (!config.features[feature]) {
      return <>{fallback}</>
    }

    return (
      <Suspense fallback={<div>Loading...</div>}>
        <Component {...props} />
      </Suspense>
    )
  }
}

// React 19 hook for feature flags
export function useFeatureFlag(feature: keyof typeof config.features) {
  return config.features[feature]
}

// Enhanced context hook with React 19 patterns
export function useAppContext() {
  const appState = useAppStore()
  
  return {
    ...appState,
    config,
    logger,
    isOnline: appState.isOnline,
    isDevelopment: config.isDevelopment,
    isProduction: config.isProduction,
    react19: {
      startTransition,
      use,
    },
  }
}

// Provider for testing with React 19 features
export function TestProviders({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary>
      <QueryProvider>
        <Suspense fallback={<div>Loading test...</div>}>
          {children}
        </Suspense>
      </QueryProvider>
    </ErrorBoundary>
  )
}
