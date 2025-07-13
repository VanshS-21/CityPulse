import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// Enhanced types for React 19 compatibility
export interface User {
  id: string
  name: string
  email: string
  role: 'citizen' | 'admin' | 'moderator'
  avatar?: string
  preferences?: {
    notifications: boolean
    theme: 'light' | 'dark' | 'system'
    language: string
  }
  metadata?: Record<string, any>
}

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title?: string
  message: string
  timestamp: number
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
  persistent?: boolean
}

export interface AppState {
  // User state
  user: User | null
  isAuthenticated: boolean

  // UI state
  theme: 'light' | 'dark' | 'system'
  sidebarOpen: boolean
  loading: boolean
  loadingStates: Record<string, boolean>

  // App state
  notifications: Notification[]

  // Connection state
  isOnline: boolean
  lastSyncTime: number | null

  // Performance tracking for React 19
  performanceMetrics: {
    pageLoadTime?: number
    apiResponseTimes: Record<string, number[]>
    errorCount: number
    renderCount: number
  }
  
  // Actions
  setUser: (user: User | null) => void
  setAuthenticated: (authenticated: boolean) => void
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  setSidebarOpen: (open: boolean) => void
  setLoading: (loading: boolean) => void
  addNotification: (notification: Omit<AppState['notifications'][0], 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void

  // Atomic operations to prevent race conditions
  updateUserProfile: (updates: Partial<User>) => void
  batchUpdateNotifications: (operations: Array<{
    type: 'add' | 'remove' | 'clear'
    notification?: Omit<AppState['notifications'][0], 'id' | 'timestamp'>
    id?: string
  }>) => void

  // Reset function
  reset: () => void
}

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  theme: 'system' as const,
  sidebarOpen: false,
  loading: false,
  notifications: []
}

// Create the store with immer for safe mutations
export const useAppStore = create<AppState>()(
  devtools(
    persist(
      immer((set, get) => ({
        ...initialState,
        
        // User actions with atomic updates
        setUser: (user) => set((state) => {
          state.user = user
          state.isAuthenticated = !!user
        }),

        setAuthenticated: (authenticated) => set((state) => {
          state.isAuthenticated = authenticated
          if (!authenticated) {
            state.user = null
          }
        }),
        
        // UI actions with immer mutations
        setTheme: (theme) => set((state) => {
          state.theme = theme
        }),

        setSidebarOpen: (open) => set((state) => {
          state.sidebarOpen = open
        }),

        setLoading: (loading) => set((state) => {
          state.loading = loading
        }),
        
        // Notification actions with race condition prevention
        addNotification: (notification) => set((state) => {
          const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
          state.notifications.push({
            ...notification,
            id,
            timestamp: Date.now()
          })

          // Limit notifications to prevent memory issues
          if (state.notifications.length > 50) {
            state.notifications = state.notifications.slice(-50)
          }
        }),

        removeNotification: (id) => set((state) => {
          const index = state.notifications.findIndex(n => n.id === id)
          if (index !== -1) {
            state.notifications.splice(index, 1)
          }
        }),

        clearNotifications: () => set((state) => {
          state.notifications = []
        }),

        // Atomic operations to prevent race conditions
        updateUserProfile: (updates) => set((state) => {
          if (state.user) {
            Object.assign(state.user, updates)
          }
        }),

        batchUpdateNotifications: (operations) => set((state) => {
          operations.forEach(operation => {
            switch (operation.type) {
              case 'add':
                if (operation.notification) {
                  const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
                  state.notifications.push({
                    ...operation.notification,
                    id,
                    timestamp: Date.now()
                  })
                }
                break
              case 'remove':
                if (operation.id) {
                  const index = state.notifications.findIndex(n => n.id === operation.id)
                  if (index !== -1) {
                    state.notifications.splice(index, 1)
                  }
                }
                break
              case 'clear':
                state.notifications = []
                break
            }
          })

          // Limit notifications after batch operations
          if (state.notifications.length > 50) {
            state.notifications = state.notifications.slice(-50)
          }
        }),

        // Reset function
        reset: () => set(() => ({ ...initialState }))
      }),
      {
        name: 'citypulse-app-store',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          theme: state.theme,
          sidebarOpen: state.sidebarOpen
        })
      }
    )
  )
)

// Selectors for optimized re-renders
export const useUser = () => useAppStore((state) => state.user)
export const useIsAuthenticated = () => useAppStore((state) => state.isAuthenticated)
export const useTheme = () => useAppStore((state) => state.theme)
export const useSidebarOpen = () => useAppStore((state) => state.sidebarOpen)
export const useLoading = () => useAppStore((state) => state.loading)
export const useNotifications = () => useAppStore((state) => state.notifications)

// Action selectors
export const useAppActions = () => useAppStore((state) => ({
  setUser: state.setUser,
  setAuthenticated: state.setAuthenticated,
  setTheme: state.setTheme,
  setSidebarOpen: state.setSidebarOpen,
  setLoading: state.setLoading,
  addNotification: state.addNotification,
  removeNotification: state.removeNotification,
  clearNotifications: state.clearNotifications,
  updateUserProfile: state.updateUserProfile,
  batchUpdateNotifications: state.batchUpdateNotifications,
  reset: state.reset
}))
