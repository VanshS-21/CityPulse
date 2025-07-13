/**
 * Application Store
 */

import { create } from 'zustand'

interface Notification {
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
}

interface AppState {
  user: any
  notifications: Notification[]
  isOnline: boolean
  addNotification?: (notification: Notification) => void
  addPerformanceMetric?: (metric: string, value: number) => void
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  notifications: [],
  isOnline: true,
  addNotification: (notification) =>
    set((state) => ({
      notifications: [...state.notifications, notification],
    })),
  addPerformanceMetric: (metric, value) => {
    // Mock implementation for testing
    console.log(`Performance metric: ${metric} = ${value}`)
  },
}))
