# CityPulse Component Library Specifications
## Modern UI Components with Glassmorphism & Accessibility

*Comprehensive component specifications based on award-winning design patterns and shadcn/ui foundation*

---

## 🎯 Design System Overview

### Foundation
- **Base Library**: shadcn/ui with Radix UI primitives
- **Styling**: Tailwind CSS with custom design tokens
- **Animation**: Framer Motion for complex animations
- **Icons**: Lucide React with custom urban-themed icons
- **Typography**: Inter font family with urban display fonts

### Design Principles
- **Glassmorphism**: Translucent surfaces with backdrop blur
- **Accessibility First**: WCAG 2.1 AA compliance built-in
- **Performance**: Optimized for 60fps animations
- **Consistency**: Unified design language across all components
- **Scalability**: Components that work at any scale

---

## 🧩 Core Component Specifications

### 1. GlassCard Component
```typescript
interface GlassCardProps {
  children: React.ReactNode
  variant: 'default' | 'elevated' | 'interactive'
  blur?: 'sm' | 'md' | 'lg' | 'xl'
  opacity?: number
  className?: string
  onClick?: () => void
}
```

**Visual Design:**
```css
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.glass-card-elevated {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(30px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.glass-card-interactive:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
}
```

**Usage Examples:**
```tsx
<GlassCard variant="elevated" blur="lg">
  <h3>Statistics Card</h3>
  <p>Content with glassmorphism effect</p>
</GlassCard>
```

### 2. AnimatedCounter Component
```typescript
interface AnimatedCounterProps {
  value: number
  duration?: number
  format?: (value: number) => string
  trigger?: 'viewport' | 'mount' | 'manual'
  onComplete?: () => void
}
```

**Implementation:**
```tsx
const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  value,
  duration = 2000,
  format = (n) => n.toLocaleString(),
  trigger = 'viewport'
}) => {
  const [count, setCount] = useState(0)
  const [isVisible, setIsVisible] = useState(false)
  const ref = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    if (trigger === 'viewport') {
      const observer = new IntersectionObserver(
        ([entry]) => setIsVisible(entry.isIntersecting),
        { threshold: 0.5 }
      )
      if (ref.current) observer.observe(ref.current)
      return () => observer.disconnect()
    }
  }, [trigger])

  useEffect(() => {
    if (isVisible || trigger !== 'viewport') {
      const startTime = Date.now()
      const animate = () => {
        const elapsed = Date.now() - startTime
        const progress = Math.min(elapsed / duration, 1)
        const easeOut = 1 - Math.pow(1 - progress, 3)
        setCount(Math.floor(value * easeOut))
        
        if (progress < 1) {
          requestAnimationFrame(animate)
        }
      }
      animate()
    }
  }, [isVisible, value, duration])

  return <span ref={ref}>{format(count)}</span>
}
```

### 3. InteractiveMap Component
```typescript
interface InteractiveMapProps {
  center: { lat: number; lng: number }
  zoom: number
  markers: MapMarker[]
  onMarkerClick: (marker: MapMarker) => void
  onMapClick: (coordinates: { lat: number; lng: number }) => void
  showClustering?: boolean
  showHeatmap?: boolean
  customStyles?: google.maps.MapTypeStyle[]
}

interface MapMarker {
  id: string
  position: { lat: number; lng: number }
  title: string
  category: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  status: 'pending' | 'in-progress' | 'resolved'
  icon?: string
}
```

**Custom Marker Styles:**
```css
.map-marker {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.marker-high {
  background: #ef4444;
  animation: pulse 2s infinite;
}

.marker-medium { background: #f59e0b; }
.marker-low { background: #10b981; }

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
```

### 4. MediaUpload Component
```typescript
interface MediaUploadProps {
  onFilesAdd: (files: File[]) => void
  onFileRemove: (index: number) => void
  maxFiles?: number
  maxSize?: number // in bytes
  acceptedTypes: string[]
  showPreview?: boolean
  dragDropText?: string
}
```

**Drag & Drop Implementation:**
```tsx
const MediaUpload: React.FC<MediaUploadProps> = ({
  onFilesAdd,
  maxFiles = 5,
  maxSize = 10 * 1024 * 1024, // 10MB
  acceptedTypes = ['image/*', 'video/*']
}) => {
  const [isDragging, setIsDragging] = useState(false)
  const [files, setFiles] = useState<File[]>([])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    const validFiles = droppedFiles.filter(file => 
      acceptedTypes.some(type => file.type.match(type)) &&
      file.size <= maxSize
    )
    
    if (files.length + validFiles.length <= maxFiles) {
      setFiles(prev => [...prev, ...validFiles])
      onFilesAdd(validFiles)
    }
  }, [files, maxFiles, maxSize, acceptedTypes, onFilesAdd])

  return (
    <div
      className={`upload-area ${isDragging ? 'dragging' : ''}`}
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      onDragEnter={() => setIsDragging(true)}
      onDragLeave={() => setIsDragging(false)}
    >
      <div className="upload-content">
        <Camera size={48} />
        <p>Drag photos here or click to browse</p>
        <p className="text-sm text-muted-foreground">
          Supports: {acceptedTypes.join(', ')} (max {maxSize / 1024 / 1024}MB each)
        </p>
      </div>
    </div>
  )
}
```

### 5. StatusTimeline Component
```typescript
interface StatusTimelineProps {
  events: TimelineEvent[]
  currentStatus: string
  orientation?: 'vertical' | 'horizontal'
  showTimestamps?: boolean
}

interface TimelineEvent {
  id: string
  status: string
  title: string
  description?: string
  timestamp: Date
  user?: string
  isCompleted: boolean
  isCurrent: boolean
}
```

**Timeline Styling:**
```css
.timeline {
  position: relative;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 20px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, #3b82f6, #e5e7eb);
}

.timeline-item {
  position: relative;
  padding-left: 50px;
  margin-bottom: 24px;
}

.timeline-marker {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid white;
  background: #3b82f6;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.timeline-marker.completed {
  background: #10b981;
}

.timeline-marker.current {
  background: #f59e0b;
  animation: pulse 2s infinite;
}
```

### 6. CategorySelector Component
```typescript
interface CategorySelectorProps {
  categories: Category[]
  selectedCategory?: string
  onSelect: (categoryId: string) => void
  layout?: 'grid' | 'list'
  showSubcategories?: boolean
}

interface Category {
  id: string
  name: string
  icon: string
  description: string
  color: string
  subcategories?: Subcategory[]
}
```

**Grid Layout:**
```tsx
const CategorySelector: React.FC<CategorySelectorProps> = ({
  categories,
  selectedCategory,
  onSelect,
  layout = 'grid'
}) => {
  return (
    <div className={`category-selector ${layout}`}>
      {categories.map(category => (
        <GlassCard
          key={category.id}
          variant="interactive"
          className={`category-card ${
            selectedCategory === category.id ? 'selected' : ''
          }`}
          onClick={() => onSelect(category.id)}
        >
          <div className="category-icon" style={{ color: category.color }}>
            {category.icon}
          </div>
          <h3 className="category-name">{category.name}</h3>
          <p className="category-description">{category.description}</p>
        </GlassCard>
      ))}
    </div>
  )
}
```

---

## 🎨 Advanced Components

### 7. DataVisualization Component
```typescript
interface DataVisualizationProps {
  type: 'bar' | 'line' | 'pie' | 'heatmap'
  data: ChartData
  options?: ChartOptions
  responsive?: boolean
  animated?: boolean
}
```

**Chart Integration:**
```tsx
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement } from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement)

const DataVisualization: React.FC<DataVisualizationProps> = ({
  type,
  data,
  animated = true
}) => {
  const chartOptions = {
    responsive: true,
    animation: animated ? {
      duration: 1000,
      easing: 'easeOutQuart'
    } : false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    }
  }

  return (
    <GlassCard className="chart-container">
      <Bar data={data} options={chartOptions} />
    </GlassCard>
  )
}
```

### 8. SearchWithFilters Component
```typescript
interface SearchWithFiltersProps {
  onSearch: (query: string) => void
  onFilterChange: (filters: FilterState) => void
  filters: FilterConfig[]
  placeholder?: string
  showRecentSearches?: boolean
}

interface FilterConfig {
  id: string
  label: string
  type: 'select' | 'multiselect' | 'date' | 'range'
  options?: FilterOption[]
}
```

**Search Implementation:**
```tsx
const SearchWithFilters: React.FC<SearchWithFiltersProps> = ({
  onSearch,
  onFilterChange,
  filters
}) => {
  const [query, setQuery] = useState('')
  const [activeFilters, setActiveFilters] = useState<FilterState>({})
  const [showFilters, setShowFilters] = useState(false)

  const debouncedSearch = useMemo(
    () => debounce((searchQuery: string) => onSearch(searchQuery), 300),
    [onSearch]
  )

  useEffect(() => {
    debouncedSearch(query)
  }, [query, debouncedSearch])

  return (
    <div className="search-container">
      <div className="search-input-wrapper">
        <Search className="search-icon" size={20} />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search issues..."
          className="search-input"
        />
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="filter-toggle"
        >
          <Filter size={20} />
          {Object.keys(activeFilters).length > 0 && (
            <span className="filter-count">
              {Object.keys(activeFilters).length}
            </span>
          )}
        </button>
      </div>
      
      {showFilters && (
        <div className="filter-panel">
          {filters.map(filter => (
            <FilterComponent
              key={filter.id}
              config={filter}
              value={activeFilters[filter.id]}
              onChange={(value) => {
                const newFilters = { ...activeFilters, [filter.id]: value }
                setActiveFilters(newFilters)
                onFilterChange(newFilters)
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
```

---

## 🎭 Animation System

### Motion Variants
```typescript
export const motionVariants = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 }
  },
  
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  },
  
  scaleIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 }
  },
  
  stagger: {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  }
}
```

### Transition Presets
```typescript
export const transitions = {
  smooth: { duration: 0.3, ease: [0.4, 0, 0.2, 1] },
  bouncy: { type: 'spring', stiffness: 300, damping: 30 },
  slow: { duration: 0.5, ease: 'easeOut' }
}
```

---

## ♿ Accessibility Implementation

### Focus Management
```typescript
export const useFocusManagement = () => {
  const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  
  const trapFocus = (container: HTMLElement) => {
    const focusable = container.querySelectorAll(focusableElements)
    const firstFocusable = focusable[0] as HTMLElement
    const lastFocusable = focusable[focusable.length - 1] as HTMLElement

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstFocusable) {
            lastFocusable.focus()
            e.preventDefault()
          }
        } else {
          if (document.activeElement === lastFocusable) {
            firstFocusable.focus()
            e.preventDefault()
          }
        }
      }
    }

    container.addEventListener('keydown', handleKeyDown)
    return () => container.removeEventListener('keydown', handleKeyDown)
  }

  return { trapFocus }
}
```

### ARIA Helpers
```typescript
export const ariaHelpers = {
  announceToScreenReader: (message: string) => {
    const announcement = document.createElement('div')
    announcement.setAttribute('aria-live', 'polite')
    announcement.setAttribute('aria-atomic', 'true')
    announcement.className = 'sr-only'
    announcement.textContent = message
    
    document.body.appendChild(announcement)
    setTimeout(() => document.body.removeChild(announcement), 1000)
  },
  
  generateId: (prefix: string) => `${prefix}-${Math.random().toString(36).substr(2, 9)}`,
  
  getAriaLabel: (element: string, context?: string) => {
    const labels = {
      'close-button': 'Close dialog',
      'menu-button': 'Open menu',
      'search-input': 'Search issues',
      'filter-button': 'Open filters'
    }
    return context ? `${labels[element]} ${context}` : labels[element]
  }
}
```

---

## 📊 Performance Optimization

### Lazy Loading
```typescript
export const LazyComponent = React.lazy(() => import('./Component'))

export const withLazyLoading = <P extends object>(
  Component: React.ComponentType<P>
) => {
  return React.forwardRef<any, P>((props, ref) => (
    <Suspense fallback={<ComponentSkeleton />}>
      <Component {...props} ref={ref} />
    </Suspense>
  ))
}
```

### Memoization Patterns
```typescript
export const MemoizedComponent = React.memo<ComponentProps>(
  ({ data, onAction }) => {
    const processedData = useMemo(
      () => expensiveDataProcessing(data),
      [data]
    )
    
    const handleAction = useCallback(
      (id: string) => onAction(id),
      [onAction]
    )
    
    return (
      <div>
        {processedData.map(item => (
          <Item key={item.id} data={item} onClick={handleAction} />
        ))}
      </div>
    )
  },
  (prevProps, nextProps) => {
    return prevProps.data === nextProps.data
  }
)
```

---

## 🧪 Testing Utilities

### Component Testing Helpers
```typescript
export const renderWithProviders = (
  ui: React.ReactElement,
  options?: RenderOptions
) => {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClient>
      <ThemeProvider>
        <MotionConfig reducedMotion="user">
          {children}
        </MotionConfig>
      </ThemeProvider>
    </QueryClient>
  )
  
  return render(ui, { wrapper: Wrapper, ...options })
}

export const mockIntersectionObserver = () => {
  global.IntersectionObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn()
  }))
}
```

This component library provides a comprehensive foundation for building the CityPulse interface with modern design patterns, excellent accessibility, and optimal performance.
