// Core application types

export interface User {
  id: string
  email: string
  name: string | null
  avatar?: string
  role: 'citizen' | 'admin' | 'moderator'
  createdAt: Date
  updatedAt: Date
}

export interface Issue {
  id: string
  title: string
  description: string
  category: IssueCategory
  priority: IssuePriority
  status: IssueStatus
  location: Location
  images: string[]
  reportedBy: string
  assignedTo?: string
  createdAt: Date
  updatedAt: Date
  resolvedAt?: Date
  tags: string[]
  upvotes: number
  downvotes: number
}

// Backend-compatible interface (snake_case)
export interface EventCore {
  id: string
  title: string
  description: string
  category: IssueCategory
  severity: IssuePriority // Maps to priority
  status: IssueStatus
  location: {
    latitude: number
    longitude: number
    address: string
    city: string
    state: string
    postal_code: string // Maps to zipCode
  }
  images?: string[]
  user_id: string // Maps to reportedBy
  assigned_to?: string // Maps to assignedTo
  created_at: string // ISO string
  updated_at: string // ISO string
  resolved_at?: string // ISO string
  tags?: string[]
  metadata?: Record<string, any>
}

export interface Location {
  latitude: number
  longitude: number
  address: string
  city: string
  state: string
  zipCode: string
}

export type IssueCategory =
  | 'infrastructure'
  | 'transportation'
  | 'environment'
  | 'safety'
  | 'utilities'
  | 'other'

export type IssuePriority = 'low' | 'medium' | 'high' | 'critical'

export type IssueStatus =
  | 'open'
  | 'in_progress'
  | 'resolved'
  | 'closed'
  | 'duplicate'

export interface Comment {
  id: string
  issueId: string
  userId: string
  content: string
  createdAt: Date
  updatedAt: Date
}

export interface Notification {
  id: string
  userId: string
  title: string
  message: string
  type: 'info' | 'warning' | 'error' | 'success'
  read: boolean
  createdAt: Date
}

export interface AnalyticsData {
  totalIssues: number
  resolvedIssues: number
  pendingIssues: number
  averageResolutionTime: number
  issuesByCategory: Record<IssueCategory, number>
  issuesByPriority: Record<IssuePriority, number>
  trendsData: TrendData[]
}

export interface TrendData {
  date: string
  issues: number
  resolved: number
}

export interface ApiResponse<T> {
  data: T
  message: string
  success: boolean
  error?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

// Form types
export interface CreateIssueForm {
  title: string
  description: string
  category: IssueCategory
  priority: IssuePriority
  location: Location
  images: File[]
  tags: string[]
}

export interface UpdateIssueForm {
  title?: string
  description?: string
  category?: IssueCategory
  priority?: IssuePriority
  status?: IssueStatus
  assignedTo?: string
  tags?: string[]
}

// Component props types
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

export interface LoadingState {
  isLoading: boolean
  error?: string
}

// API endpoints
export interface ApiEndpoints {
  issues: string
  users: string
  analytics: string
  notifications: string
  auth: string
}
