# CityPulse Public Issue Discovery Wireframe
## Interactive Map & List View with Advanced Filtering

*Inspired by modern data exploration interfaces with seamless view switching and real-time updates*

---

## 🎯 Design Overview

### Inspiration Sources
- **Data Visualization Platforms**: Clean, scannable information displays
- **Map-Based Applications**: Seamless map/list view transitions
- **Modern Filtering**: Intuitive filter interfaces with visual feedback
- **Real-time Updates**: Live data with smooth animations

### Design Principles
- **Information Accessibility**: Public transparency without barriers
- **Visual Hierarchy**: Clear issue prioritization and status
- **Contextual Navigation**: Location-aware browsing experience
- **Performance**: Fast loading with progressive enhancement

---

## 📱 Layout Structure

### Desktop Layout (1200px+)
```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER: Logo | Navigation | Search | [Login]                   │
├─────────────────────────────────────────────────────────────────┤
│ FILTER BAR                                                      │
│ [🔍 Search] [📍 Location] [📂 Category] [🔄 Status] [📅 Date] │
│ Active Filters: Road Issues × | High Priority × | This Week ×  │
├─────────────────────────────────────────────────────────────────┤
│ VIEW CONTROLS                                                   │
│ [🗺️ Map View] [📋 List View] | Sort: [Recent ▼] | 1,247 issues │
├─────────────────────────────────────────────────────────────────┤
│ MAIN CONTENT (Split View)                                       │
│ ┌─────────────────────────────┐ ┌─────────────────────────────┐ │
│ │ ISSUE LIST (40% width)      │ │ INTERACTIVE MAP (60%)       │ │
│ │                             │ │                             │ │
│ │ ┌─────────────────────────┐ │ │ ┌─────────────────────────┐ │ │
│ │ │ ISSUE CARD              │ │ │ │                         │ │ │
│ │ │ 🚧 Large pothole        │ │ │ │                         │ │ │
│ │ │ 📍 Main St, Downtown    │ │ │ │    GOOGLE MAPS          │ │ │
│ │ │ ⏰ 2 hours ago          │ │ │ │    with clustered       │ │ │
│ │ │ 🔴 High Priority        │ │ │ │    issue markers        │ │ │
│ │ │ 👁️ 23 views            │ │ │ │                         │ │ │
│ │ └─────────────────────────┘ │ │ └─────────────────────────┘ │ │
│ │                             │ │                             │ │
│ │ ┌─────────────────────────┐ │ │ MAP CONTROLS:               │ │
│ │ │ ISSUE CARD              │ │ │ [🎯] Center on Location    │ │
│ │ │ 💡 Broken street light  │ │ │ [📊] Show Heatmap          │ │
│ │ │ 📍 Oak Ave, Midtown     │ │ │ [🔍] Zoom Controls         │ │
│ │ │ ⏰ 5 hours ago          │ │ │ [📱] Mobile View           │ │
│ │ │ 🟡 Medium Priority      │ │ │                             │ │
│ │ │ 👁️ 15 views            │ │ │ LEGEND:                     │ │
│ │ └─────────────────────────┘ │ │ 🔴 High  🟡 Medium  🟢 Low │ │
│ │                             │ │ ✅ Resolved  ⏳ In Progress │ │
│ │ [Load More Issues...]       │ │                             │ │
│ └─────────────────────────────┘ └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ FOOTER: About | Contact | API | Terms                          │
└─────────────────────────────────────────────────────────────────┘
```

### Mobile Layout (320px-768px)
```
┌─────────────────────────────────┐
│ HEADER: [☰] CityPulse [🔍]      │
├─────────────────────────────────┤
│ SEARCH & FILTERS                │
│ ┌─────────────────────────────┐ │
│ │ [🔍 Search issues...]       │ │
│ └─────────────────────────────┘ │
│ [📂 Filters (3)] [📍 Near Me]  │
├─────────────────────────────────┤
│ VIEW TOGGLE                     │
│ [📋 List] [🗺️ Map] | 1,247 total │
├─────────────────────────────────┤
│ CONTENT (Single View)           │
│ ┌─────────────────────────────┐ │
│ │ LIST VIEW                   │ │
│ │                             │ │
│ │ ┌─────────────────────────┐ │ │
│ │ │ 🚧 Large pothole        │ │ │
│ │ │ Main St, Downtown       │ │ │
│ │ │ 2h ago • High • 23 views│ │ │
│ │ │ [📷] [👁️ View Details]   │ │ │
│ │ └─────────────────────────┘ │ │
│ │                             │ │
│ │ ┌─────────────────────────┐ │ │
│ │ │ 💡 Broken street light  │ │ │
│ │ │ Oak Ave, Midtown        │ │ │
│ │ │ 5h ago • Med • 15 views │ │ │
│ │ │ [📷] [👁️ View Details]   │ │ │
│ │ └─────────────────────────┘ │ │
│ │                             │ │
│ │ [Load More...]              │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ FLOATING ACTION                 │
│ [📍 Show on Map]                │
└─────────────────────────────────┘
```

---

## 🎨 Component Specifications

### Filter Bar Component
```typescript
interface FilterBarProps {
  filters: {
    search: string
    location: string
    category: string[]
    status: string[]
    dateRange: DateRange
  }
  onFilterChange: (filters: Partial<FilterState>) => void
  activeCount: number
}
```

**Visual Design:**
- **Filter Chips**: Glassmorphism style with clear labels
- **Active Indicators**: Badge count on filter buttons
- **Clear Actions**: Individual and "Clear All" options
- **Responsive**: Collapsible on mobile with drawer

**Filter Types:**
```typescript
const filterOptions = {
  categories: [
    { id: 'road', name: 'Road Issues', icon: '🚧', color: 'orange' },
    { id: 'lighting', name: 'Street Lights', icon: '💡', color: 'yellow' },
    { id: 'waste', name: 'Waste Management', icon: '🚮', color: 'green' },
    { id: 'parks', name: 'Parks & Trees', icon: '🌳', color: 'emerald' },
    { id: 'water', name: 'Water Issues', icon: '🚰', color: 'blue' },
    { id: 'traffic', name: 'Traffic Signals', icon: '🚦', color: 'red' }
  ],
  statuses: [
    { id: 'reported', name: 'Reported', color: 'gray' },
    { id: 'in-progress', name: 'In Progress', color: 'blue' },
    { id: 'resolved', name: 'Resolved', color: 'green' },
    { id: 'closed', name: 'Closed', color: 'slate' }
  ],
  priorities: [
    { id: 'low', name: 'Low', color: 'green' },
    { id: 'medium', name: 'Medium', color: 'yellow' },
    { id: 'high', name: 'High', color: 'orange' },
    { id: 'urgent', name: 'Urgent', color: 'red' }
  ]
}
```

### Issue Card Component
```typescript
interface IssueCardProps {
  issue: PublicIssue
  onView: (issueId: string) => void
  onMapFocus: (coordinates: Coordinates) => void
  compact?: boolean
}

interface PublicIssue {
  id: string
  title: string
  category: string
  location: {
    address: string
    coordinates: { lat: number; lng: number }
  }
  status: 'reported' | 'in-progress' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  createdAt: Date
  viewCount: number
  hasMedia: boolean
  description?: string // Truncated for list view
}
```

**Visual Design:**
- **Card Layout**: Glassmorphism with subtle shadows
- **Status Indicators**: Color-coded priority and status badges
- **Media Indicators**: Icons showing photo/video availability
- **Interaction Hints**: Hover effects and clear CTAs

**Card States:**
- **Default**: Clean, scannable layout
- **Hover**: Subtle lift with increased shadow
- **Selected**: Border highlight when focused from map
- **Loading**: Skeleton animation during data fetch

### Interactive Map Component
```typescript
interface InteractiveMapProps {
  issues: PublicIssue[]
  selectedIssue?: string
  onIssueSelect: (issueId: string) => void
  onMapMove: (bounds: MapBounds) => void
  showHeatmap?: boolean
}
```

**Map Features:**
- **Marker Clustering**: Group nearby issues for performance
- **Custom Markers**: Category-specific icons with priority colors
- **Info Windows**: Quick issue preview on marker click
- **Heatmap Layer**: Density visualization toggle
- **Responsive Zoom**: Automatic bounds adjustment

**Marker Design:**
```css
/* Priority-based marker styling */
.marker-high { 
  background: #ef4444; 
  border: 2px solid #dc2626;
  animation: pulse 2s infinite;
}
.marker-medium { 
  background: #f59e0b; 
  border: 2px solid #d97706;
}
.marker-low { 
  background: #10b981; 
  border: 2px solid #059669;
}
```

### View Toggle Component
```typescript
interface ViewToggleProps {
  currentView: 'list' | 'map' | 'split'
  onViewChange: (view: ViewType) => void
  issueCount: number
}
```

**Visual Design:**
- **Toggle Buttons**: Clear active/inactive states
- **Issue Counter**: Real-time count with filter updates
- **Sort Options**: Dropdown with common sorting methods
- **Responsive**: Adapts layout options by screen size

---

## 🎭 Animation Specifications

### View Transitions
```css
/* List to map transition */
@keyframes viewTransition {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Issue card stagger animation */
.issue-card:nth-child(n) {
  animation: slideUp 0.3s ease-out;
  animation-delay: calc(var(--index) * 50ms);
}

/* Map marker drop animation */
@keyframes markerDrop {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

### Loading States
- **Skeleton Cards**: Shimmer animation during data load
- **Map Loading**: Spinner overlay with progress indicator
- **Filter Updates**: Smooth transition between result sets
- **Infinite Scroll**: Loading indicator at list bottom

### Micro-interactions
- **Filter Chips**: Scale animation on selection
- **Card Hover**: Lift effect with shadow increase
- **Map Markers**: Bounce animation on selection
- **Search**: Debounced input with loading indicator

---

## 🔍 Search & Discovery Features

### Search Implementation
```typescript
interface SearchConfig {
  fields: ['title', 'description', 'location.address']
  fuzzySearch: boolean
  autocomplete: boolean
  recentSearches: boolean
  searchHistory: boolean
}
```

**Search Features:**
- **Full-text Search**: Title, description, and location
- **Autocomplete**: Real-time suggestions as user types
- **Recent Searches**: Quick access to previous queries
- **Search Filters**: Combine text search with category filters
- **Geospatial Search**: "Near me" and radius-based filtering

### Discovery Patterns
- **Trending Issues**: Most viewed or reported issues
- **Nearby Issues**: Location-based recommendations
- **Category Browsing**: Explore by issue type
- **Time-based Views**: Recent, this week, this month
- **Status Updates**: Follow issue resolution progress

---

## 📱 Responsive Behavior

### Breakpoint Adaptations
```css
/* Desktop (1200px+) */
.discovery-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 1rem;
}

/* Tablet (768px-1200px) */
.discovery-layout {
  grid-template-columns: 1fr;
  grid-template-rows: auto 1fr;
}

/* Mobile (320px-768px) */
.discovery-layout {
  display: block;
}
.view-toggle {
  position: sticky;
  top: 0;
  z-index: 10;
}
```

### Mobile Optimizations
- **Touch-Friendly**: 44px minimum touch targets
- **Swipe Gestures**: Swipe between list and map views
- **Pull-to-Refresh**: Native refresh gesture support
- **Infinite Scroll**: Performance-optimized list loading

---

## ♿ Accessibility Features

### WCAG 2.1 AA Compliance
- **Keyboard Navigation**: Full keyboard support for all interactions
- **Screen Reader**: Proper ARIA labels and live regions
- **Color Contrast**: 4.5:1 ratio for all text elements
- **Focus Management**: Clear focus indicators and logical tab order

### Implementation Details
```typescript
// Screen reader announcements
const announceResults = (count: number) => {
  const message = `${count} issues found. Use arrow keys to navigate.`
  setLiveRegion(message)
}

// Keyboard shortcuts
const keyboardShortcuts = {
  'Ctrl+F': 'Focus search input',
  'M': 'Toggle map view',
  'L': 'Toggle list view',
  'Escape': 'Clear filters'
}
```

---

## 📊 Performance Optimization

### Data Loading Strategy
- **Pagination**: Load 20 issues per page with infinite scroll
- **Clustering**: Group nearby markers for map performance
- **Caching**: Cache issue data with 5-minute TTL
- **Prefetching**: Load next page data on scroll proximity

### Bundle Optimization
- **Code Splitting**: Separate bundles for map and list components
- **Lazy Loading**: Load map library only when needed
- **Image Optimization**: WebP format with lazy loading
- **Service Worker**: Cache static assets and API responses

---

## 📈 Success Metrics

### User Engagement
- **Discovery Rate**: % of users who explore multiple issues
- **View Duration**: Average time spent viewing issues
- **Filter Usage**: % of users who apply filters
- **Map Interaction**: % of users who interact with map

### Technical Performance
- **Load Time**: < 2s for initial page load
- **Search Speed**: < 300ms for search results
- **Map Performance**: 60fps during interactions
- **Mobile Performance**: < 3s on 3G networks

This public discovery wireframe creates an accessible, performant interface that enables citizens to explore community issues while maintaining transparency and encouraging civic engagement.
