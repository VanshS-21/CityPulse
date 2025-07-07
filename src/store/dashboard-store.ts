/**
 * Enhanced Dashboard State Management with Zustand
 * Implements granular state management following 2025 best practices
 */

import { create } from 'zustand';
import { subscribeWithSelector, devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

// Types for different state slices
interface MetricsState {
  totalReports: number;
  resolvedReports: number;
  pendingReports: number;
  avgResponseTime: number;
  criticalIssues: number;
  lastUpdated: string | null;
  loading: boolean;
  error: string | null;
}

interface FilterState {
  dateRange: 'day' | 'week' | 'month' | 'year';
  category: 'all' | 'infrastructure' | 'safety' | 'environment' | 'other';
  status: 'all' | 'pending' | 'in_progress' | 'resolved' | 'closed';
  priority: 'all' | 'low' | 'medium' | 'high' | 'critical';
  location: {
    bounds: {
      north: number;
      south: number;
      east: number;
      west: number;
    } | null;
    zoom: number;
    center: { lat: number; lng: number };
  };
}

interface UIState {
  sidebarOpen: boolean;
  mapView: 'roadmap' | 'satellite' | 'hybrid' | 'terrain';
  theme: 'light' | 'dark' | 'system';
  notifications: {
    enabled: boolean;
    sound: boolean;
    desktop: boolean;
  };
  layout: 'grid' | 'list' | 'map';
  activePanel: 'overview' | 'reports' | 'analytics' | 'settings' | null;
}

interface ReportsState {
  reports: Report[];
  selectedReport: Report | null;
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasMore: boolean;
  };
}

interface Report {
  id: string;
  title: string;
  description: string;
  category: string;
  status: string;
  priority: string;
  location: {
    lat: number;
    lng: number;
    address: string;
  };
  createdAt: string;
  updatedAt: string;
  assignedTo?: string;
  images?: string[];
  metadata?: Record<string, unknown>;
}

// Main dashboard state interface
interface DashboardState {
  // State slices
  metrics: MetricsState;
  filters: FilterState;
  ui: UIState;
  reports: ReportsState;

  // Metrics actions
  updateMetrics: (metrics: Partial<MetricsState>) => void;
  setMetricsLoading: (loading: boolean) => void;
  setMetricsError: (error: string | null) => void;
  refreshMetrics: () => Promise<void>;

  // Filter actions
  setDateRange: (range: FilterState['dateRange']) => void;
  setCategory: (category: FilterState['category']) => void;
  setStatus: (status: FilterState['status']) => void;
  setPriority: (priority: FilterState['priority']) => void;
  setLocationBounds: (bounds: FilterState['location']['bounds']) => void;
  setMapCenter: (center: { lat: number; lng: number }) => void;
  setMapZoom: (zoom: number) => void;
  resetFilters: () => void;

  // UI actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setMapView: (view: UIState['mapView']) => void;
  setTheme: (theme: UIState['theme']) => void;
  setLayout: (layout: UIState['layout']) => void;
  setActivePanel: (panel: UIState['activePanel']) => void;
  updateNotificationSettings: (settings: Partial<UIState['notifications']>) => void;

  // Reports actions
  setReports: (reports: Report[]) => void;
  addReport: (report: Report) => void;
  updateReport: (id: string, updates: Partial<Report>) => void;
  removeReport: (id: string) => void;
  setSelectedReport: (report: Report | null) => void;
  setReportsLoading: (loading: boolean) => void;
  setReportsError: (error: string | null) => void;
  loadMoreReports: () => Promise<void>;
  refreshReports: () => Promise<void>;

  // Computed selectors
  getFilteredReports: () => Report[];
  getMetricsSummary: () => {
    totalReports: number;
    resolutionRate: number;
    avgResponseTime: number;
    criticalIssues: number;
  };
}

// Initial state values
const initialMetrics: MetricsState = {
  totalReports: 0,
  resolvedReports: 0,
  pendingReports: 0,
  avgResponseTime: 0,
  criticalIssues: 0,
  lastUpdated: null,
  loading: false,
  error: null,
};

const initialFilters: FilterState = {
  dateRange: 'week',
  category: 'all',
  status: 'all',
  priority: 'all',
  location: {
    bounds: null,
    zoom: 10,
    center: { lat: 40.7128, lng: -74.0060 }, // Default to NYC
  },
};

const initialUI: UIState = {
  sidebarOpen: true,
  mapView: 'roadmap',
  theme: 'system',
  notifications: {
    enabled: true,
    sound: true,
    desktop: true,
  },
  layout: 'grid',
  activePanel: 'overview',
};

const initialReports: ReportsState = {
  reports: [],
  selectedReport: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    limit: 20,
    total: 0,
    hasMore: false,
  },
};

// Create the store with middleware
export const useDashboardStore = create<DashboardState>()(
  devtools(
    persist(
      subscribeWithSelector(
        immer((set, get) => ({
          // Initial state
          metrics: initialMetrics,
          filters: initialFilters,
          ui: initialUI,
          reports: initialReports,

          // Metrics actions
          updateMetrics: (metrics) =>
            set((state) => {
              Object.assign(state.metrics, metrics);
              state.metrics.lastUpdated = new Date().toISOString();
            }),

          setMetricsLoading: (loading) =>
            set((state) => {
              state.metrics.loading = loading;
            }),

          setMetricsError: (error) =>
            set((state) => {
              state.metrics.error = error;
            }),

          refreshMetrics: async () => {
            const { setMetricsLoading, setMetricsError, updateMetrics } = get();
            
            try {
              setMetricsLoading(true);
              setMetricsError(null);
              
              // TODO: Replace with actual API call
              const response = await fetch('/api/metrics');
              const data = await response.json();
              
              updateMetrics(data);
            } catch (error) {
              setMetricsError(error instanceof Error ? error.message : 'Failed to load metrics');
            } finally {
              setMetricsLoading(false);
            }
          },

          // Filter actions
          setDateRange: (range) =>
            set((state) => {
              state.filters.dateRange = range;
            }),

          setCategory: (category) =>
            set((state) => {
              state.filters.category = category;
            }),

          setStatus: (status) =>
            set((state) => {
              state.filters.status = status;
            }),

          setPriority: (priority) =>
            set((state) => {
              state.filters.priority = priority;
            }),

          setLocationBounds: (bounds) =>
            set((state) => {
              state.filters.location.bounds = bounds;
            }),

          setMapCenter: (center) =>
            set((state) => {
              state.filters.location.center = center;
            }),

          setMapZoom: (zoom) =>
            set((state) => {
              state.filters.location.zoom = zoom;
            }),

          resetFilters: () =>
            set((state) => {
              state.filters = { ...initialFilters };
            }),

          // UI actions
          toggleSidebar: () =>
            set((state) => {
              state.ui.sidebarOpen = !state.ui.sidebarOpen;
            }),

          setSidebarOpen: (open) =>
            set((state) => {
              state.ui.sidebarOpen = open;
            }),

          setMapView: (view) =>
            set((state) => {
              state.ui.mapView = view;
            }),

          setTheme: (theme) =>
            set((state) => {
              state.ui.theme = theme;
            }),

          setLayout: (layout) =>
            set((state) => {
              state.ui.layout = layout;
            }),

          setActivePanel: (panel) =>
            set((state) => {
              state.ui.activePanel = panel;
            }),

          updateNotificationSettings: (settings) =>
            set((state) => {
              Object.assign(state.ui.notifications, settings);
            }),

          // Reports actions
          setReports: (reports) =>
            set((state) => {
              state.reports.reports = reports;
            }),

          addReport: (report) =>
            set((state) => {
              state.reports.reports.unshift(report);
            }),

          updateReport: (id, updates) =>
            set((state) => {
              const index = state.reports.reports.findIndex((r: Report) => r.id === id);
              if (index !== -1) {
                Object.assign(state.reports.reports[index], updates);
              }
            }),

          removeReport: (id) =>
            set((state) => {
              state.reports.reports = state.reports.reports.filter((r: Report) => r.id !== id);
            }),

          setSelectedReport: (report) =>
            set((state) => {
              state.reports.selectedReport = report;
            }),

          setReportsLoading: (loading) =>
            set((state) => {
              state.reports.loading = loading;
            }),

          setReportsError: (error) =>
            set((state) => {
              state.reports.error = error;
            }),

          loadMoreReports: async () => {
            // TODO: Implement pagination loading
          },

          refreshReports: async () => {
            // TODO: Implement reports refresh
          },

          // Computed selectors
          getFilteredReports: () => {
            const { reports, filters } = get();
            
            return reports.reports.filter((report) => {
              // Apply category filter
              if (filters.category !== 'all' && report.category !== filters.category) {
                return false;
              }
              
              // Apply status filter
              if (filters.status !== 'all' && report.status !== filters.status) {
                return false;
              }
              
              // Apply priority filter
              if (filters.priority !== 'all' && report.priority !== filters.priority) {
                return false;
              }
              
              // Apply date range filter
              const reportDate = new Date(report.createdAt);
              const now = new Date();
              const daysDiff = Math.floor((now.getTime() - reportDate.getTime()) / (1000 * 60 * 60 * 24));
              
              switch (filters.dateRange) {
                case 'day':
                  if (daysDiff > 1) return false;
                  break;
                case 'week':
                  if (daysDiff > 7) return false;
                  break;
                case 'month':
                  if (daysDiff > 30) return false;
                  break;
                case 'year':
                  if (daysDiff > 365) return false;
                  break;
              }
              
              return true;
            });
          },

          getMetricsSummary: () => {
            const { metrics } = get();
            
            return {
              totalReports: metrics.totalReports,
              resolutionRate: metrics.totalReports > 0 
                ? Math.round((metrics.resolvedReports / metrics.totalReports) * 100) 
                : 0,
              avgResponseTime: metrics.avgResponseTime,
              criticalIssues: metrics.criticalIssues,
            };
          },
        }))
      ),
      {
        name: 'citypulse-dashboard-store',
        partialize: (state) => ({
          filters: state.filters,
          ui: {
            ...state.ui,
            activePanel: null, // Don't persist active panel
          },
        }),
      }
    ),
    {
      name: 'citypulse-dashboard-store',
    }
  )
);

// Selectors for specific state slices
export const useMetrics = () => useDashboardStore((state) => state.metrics);
export const useFilters = () => useDashboardStore((state) => state.filters);
export const useUI = () => useDashboardStore((state) => state.ui);
export const useReports = () => useDashboardStore((state) => state.reports);

// Action selectors
export const useMetricsActions = () => useDashboardStore((state) => ({
  updateMetrics: state.updateMetrics,
  setMetricsLoading: state.setMetricsLoading,
  setMetricsError: state.setMetricsError,
  refreshMetrics: state.refreshMetrics,
}));

export const useFilterActions = () => useDashboardStore((state) => ({
  setDateRange: state.setDateRange,
  setCategory: state.setCategory,
  setStatus: state.setStatus,
  setPriority: state.setPriority,
  setLocationBounds: state.setLocationBounds,
  setMapCenter: state.setMapCenter,
  setMapZoom: state.setMapZoom,
  resetFilters: state.resetFilters,
}));

export const useUIActions = () => useDashboardStore((state) => ({
  toggleSidebar: state.toggleSidebar,
  setSidebarOpen: state.setSidebarOpen,
  setMapView: state.setMapView,
  setTheme: state.setTheme,
  setLayout: state.setLayout,
  setActivePanel: state.setActivePanel,
  updateNotificationSettings: state.updateNotificationSettings,
}));

export const useReportsActions = () => useDashboardStore((state) => ({
  setReports: state.setReports,
  addReport: state.addReport,
  updateReport: state.updateReport,
  removeReport: state.removeReport,
  setSelectedReport: state.setSelectedReport,
  setReportsLoading: state.setReportsLoading,
  setReportsError: state.setReportsError,
  loadMoreReports: state.loadMoreReports,
  refreshReports: state.refreshReports,
}));

// Computed selectors
export const useFilteredReports = () => useDashboardStore((state) => state.getFilteredReports());
export const useMetricsSummary = () => useDashboardStore((state) => state.getMetricsSummary());
