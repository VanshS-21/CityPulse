import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

// Types for the store
interface User {
  id: string
  name: string
  email: string
  role: 'citizen' | 'admin' | 'moderator'
}

interface AppState {
  // User state
  user: User | null
  isAuthenticated: boolean
  
  // UI state
  theme: 'light' | 'dark' | 'system'
  sidebarOpen: boolean
  loading: boolean
  
  // App state
  notifications: Array<{
    id: string
    type: 'info' | 'success' | 'warning' | 'error'
    message: string
    timestamp: number
  }>
  
  // Actions
  setUser: (user: User | null) => void
  setAuthenticated: (authenticated: boolean) => void
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  setSidebarOpen: (open: boolean) => void
  setLoading: (loading: boolean) => void
  addNotification: (notification: Omit<AppState['notifications'][0], 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void
  
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

// Create the store
export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,
        
        // User actions
        setUser: (user) => set((state) => ({
          ...state,
          user,
          isAuthenticated: !!user
        })),
        
        setAuthenticated: (authenticated) => set((state) => ({
          ...state,
          isAuthenticated: authenticated,
          user: authenticated ? state.user : null
        })),
        
        // UI actions
        setTheme: (theme) => set((state) => ({
          ...state,
          theme
        })),
        
        setSidebarOpen: (open) => set((state) => ({
          ...state,
          sidebarOpen: open
        })),
        
        setLoading: (loading) => set((state) => ({
          ...state,
          loading
        })),
        
        // Notification actions
        addNotification: (notification) => set((state) => {
          const id = Math.random().toString(36).substr(2, 9)
          return {
            ...state,
            notifications: [...state.notifications, {
              ...notification,
              id,
              timestamp: Date.now()
            }]
          }
        }),
        
        removeNotification: (id) => set((state) => ({
          ...state,
          notifications: state.notifications.filter(n => n.id !== id)
        })),
        
        clearNotifications: () => set((state) => ({
          ...state,
          notifications: []
        })),
        
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
    ),
    {
      name: 'citypulse-app-store'
    }
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
  reset: state.reset
}))
