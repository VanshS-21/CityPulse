// Application constants
import { config } from '@/lib/config'

export const APP_CONFIG = {
  name: 'CityPulse',
  version: '1.0.0',
  description: 'Urban Issue Tracking Platform',
  url: config.app.url,
  api: {
    baseUrl: '/api/v1',
    timeout: config.api.timeout,
  },
} as const

export const ROUTES = {
  home: '/',
  dashboard: '/dashboard',
  report: '/report',
  social: '/social',
  profile: '/profile',
  settings: '/settings',
  admin: '/admin',
  login: '/auth/login',
  register: '/auth/register',
} as const

export const API_ENDPOINTS = {
  issues: '/api/v1/events',
  users: '/api/v1/users',
  analytics: '/api/v1/analytics',
  notifications: '/api/v1/notifications',
  auth: '/api/v1/auth',
  upload: '/api/v1/upload',
  social: '/api/v1/social',
  ai: '/api/v1/ai',
  feedback: '/api/v1/feedback',
} as const

export const ISSUE_CATEGORIES = [
  { value: 'infrastructure', label: 'Infrastructure', icon: '🏗️' },
  { value: 'transportation', label: 'Transportation', icon: '🚗' },
  { value: 'environment', label: 'Environment', icon: '🌱' },
  { value: 'safety', label: 'Safety', icon: '🛡️' },
  { value: 'utilities', label: 'Utilities', icon: '⚡' },
  { value: 'other', label: 'Other', icon: '📝' },
] as const

export const ISSUE_PRIORITIES = [
  { value: 'low', label: 'Low', color: 'green' },
  { value: 'medium', label: 'Medium', color: 'yellow' },
  { value: 'high', label: 'High', color: 'orange' },
  { value: 'critical', label: 'Critical', color: 'red' },
] as const

export const ISSUE_STATUSES = [
  { value: 'open', label: 'Open', color: 'blue' },
  { value: 'in_progress', label: 'In Progress', color: 'yellow' },
  { value: 'resolved', label: 'Resolved', color: 'green' },
  { value: 'closed', label: 'Closed', color: 'gray' },
  { value: 'duplicate', label: 'Duplicate', color: 'purple' },
] as const

export const USER_ROLES = [
  { value: 'citizen', label: 'Citizen' },
  { value: 'moderator', label: 'Moderator' },
  { value: 'admin', label: 'Administrator' },
] as const

export const NOTIFICATION_TYPES = [
  { value: 'info', label: 'Information', color: 'blue' },
  { value: 'warning', label: 'Warning', color: 'yellow' },
  { value: 'error', label: 'Error', color: 'red' },
  { value: 'success', label: 'Success', color: 'green' },
] as const

export const PAGINATION = config.pagination

export const VALIDATION = config.validation

export const STORAGE_KEYS = {
  authToken: 'citypulse_auth_token',
  userPreferences: 'citypulse_user_preferences',
  draftIssue: 'citypulse_draft_issue',
  theme: 'citypulse_theme',
} as const

export const THEME = config.theme

export const ANALYTICS = config.analytics

export const FEATURE_FLAGS = config.features
