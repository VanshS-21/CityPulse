/**
 * Application Store
 */

import { create } from 'zustand'

interface Notification {
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
}

interface PerformanceMetrics {
  apiResponseTimes: {
    [key: string]: number[]
  }
}

interface AppState {
  user: any
  notifications: Notification[]
  isOnline: boolean
  performanceMetrics: PerformanceMetrics
  addNotification?: (notification: Notification) => void
  addPerformanceMetric?: (metric: string, value: number) => void
  setOnlineStatus?: (isOnline: boolean) => void
  reset?: () => void
}

export const useAppStore = create<AppState>((set, get) => {
  const store = {
    user: null,
    notifications: [],
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    performanceMetrics: {
      apiResponseTimes: {},
    },
    addNotification: (notification: Notification) =>
      set((state) => ({
        notifications: [...state.notifications, notification],
      })),
    addPerformanceMetric: (metric: string, value: number) => {
      set((state) => ({
        performanceMetrics: {
          ...state.performanceMetrics,
          apiResponseTimes: {
            ...state.performanceMetrics.apiResponseTimes,
            [metric]: [...(state.performanceMetrics.apiResponseTimes[metric] || []), value],
          },
        },
      }));
    },
    setOnlineStatus: (isOnline: boolean) => set({ isOnline }),
    reset: () => set({
      user: null,
      notifications: [],
      isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
      performanceMetrics: {
        apiResponseTimes: {},
      },
    }),
  };

  // Add event listeners for online/offline events
  if (typeof window !== 'undefined') {
    const handleOnline = () => {
      store.setOnlineStatus(true);
    };
    
    const handleOffline = () => {
      store.setOnlineStatus(false);
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
  }

  return store;
})
