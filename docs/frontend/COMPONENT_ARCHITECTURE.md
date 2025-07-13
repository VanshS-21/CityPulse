# CityPulse Component Architecture
## Modern React Component System with TypeScript & Accessibility

*Comprehensive component architecture based on wireframes and modern design patterns*

---

## 🏗️ Component Hierarchy

### **Foundation Layer**
```typescript
// Design System Structure from Wireframes
interface ComponentArchitecture {
  foundation: {
    tokens: DesignTokens;           // Color, typography, spacing
    utilities: UtilityClasses;     // Tailwind utilities + custom
    primitives: PrimitiveComponents; // Base building blocks
  };
  
  components: {
    base: BaseComponents;           // Button, Input, Card, etc.
    composite: CompositeComponents; // Form, Modal, Navigation
    specialized: SpecializedComponents; // Map, Charts, Upload
    layout: LayoutComponents;       // Container, Grid, Stack
  };
  
  patterns: {
    forms: FormPatterns;           // Multi-step, validation
    navigation: NavigationPatterns; // Header, sidebar, breadcrumb
    dataDisplay: DataDisplayPatterns; // Tables, cards, charts
    feedback: FeedbackPatterns;    // Alerts, toasts, loading
  };
}
```

---

## ⚛️ Primitive Components

### **Button Component**
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost' | 'outline' | 'glass';
  size: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

// Usage from wireframes
<Button variant="primary" size="lg" icon={<RocketIcon />}>
  Report an Issue
</Button>

<Button variant="glass" size="md" icon={<SearchIcon />}>
  Explore Public Issues
</Button>
```

### **Input Component**
```typescript
interface InputProps {
  type: 'text' | 'email' | 'password' | 'search' | 'tel' | 'url';
  placeholder?: string;
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
  onFocus?: () => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  helperText?: string;
  label?: string;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  size: 'sm' | 'md' | 'lg';
  variant: 'default' | 'glass' | 'minimal';
  autoComplete?: string;
  className?: string;
}

// Usage from wireframes
<Input
  type="search"
  placeholder="Search issues..."
  icon={<SearchIcon />}
  variant="glass"
  size="lg"
/>
```

### **Card Component**
```typescript
interface CardProps {
  variant: 'default' | 'glass' | 'elevated' | 'interactive';
  padding: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  shadow: 'none' | 'sm' | 'md' | 'lg' | 'glass';
  border?: boolean;
  hover?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
}

// Usage from wireframes
<Card variant="glass" padding="lg" shadow="glass" hover>
  <CardHeader>
    <CardTitle>Issues Reported</CardTitle>
  </CardHeader>
  <CardContent>
    <AnimatedCounter value={12847} />
    <TrendIndicator value={15} direction="up" />
  </CardContent>
</Card>
```

---

## 🧩 Composite Components

### **Modal Component**
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  size: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  variant: 'default' | 'glass' | 'centered';
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  children: React.ReactNode;
  className?: string;
}

// Usage from wireframes - Authentication Modal
<Modal
  isOpen={authModalOpen}
  onClose={() => setAuthModalOpen(false)}
  title="Join CityPulse"
  size="md"
  variant="glass"
>
  <AuthenticationForm />
</Modal>
```

### **Navigation Component**
```typescript
interface NavigationProps {
  variant: 'header' | 'sidebar' | 'mobile';
  items: NavigationItem[];
  currentPath: string;
  user?: User;
  onMenuToggle?: () => void;
  onUserMenuClick?: () => void;
  logo?: React.ReactNode;
  className?: string;
}

interface NavigationItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
  badge?: string | number;
  children?: NavigationItem[];
  roles?: UserRole[];
}

// Usage from wireframes
<Navigation
  variant="header"
  items={navigationItems}
  currentPath="/dashboard"
  user={currentUser}
  logo={<CityPulseLogo />}
/>
```

### **Form Component**
```typescript
interface FormProps {
  onSubmit: (data: FormData) => void | Promise<void>;
  validation?: ValidationSchema;
  loading?: boolean;
  children: React.ReactNode;
  className?: string;
}

interface MultiStepFormProps extends FormProps {
  steps: FormStep[];
  currentStep: number;
  onStepChange: (step: number) => void;
  showProgress?: boolean;
  allowStepNavigation?: boolean;
}

// Usage from wireframes - Issue Reporting
<MultiStepForm
  steps={issueReportingSteps}
  currentStep={currentStep}
  onStepChange={setCurrentStep}
  onSubmit={handleIssueSubmit}
  showProgress
>
  <LocationStep />
  <CategoryStep />
  <DetailsStep />
  <MediaStep />
  <ReviewStep />
</MultiStepForm>
```

---

## 🎯 Specialized Components

### **InteractiveMap Component**
```typescript
interface InteractiveMapProps {
  center: { lat: number; lng: number };
  zoom: number;
  markers: MapMarker[];
  onMarkerClick: (marker: MapMarker) => void;
  onMapClick?: (coordinates: LatLng) => void;
  showClustering?: boolean;
  showHeatmap?: boolean;
  showControls?: boolean;
  height?: string;
  className?: string;
}

interface MapMarker {
  id: string;
  position: { lat: number; lng: number };
  title: string;
  category: IssueCategory;
  priority: IssuePriority;
  status: IssueStatus;
  icon?: string;
  data?: any;
}

// Usage from wireframes
<InteractiveMap
  center={{ lat: 40.7128, lng: -74.0060 }}
  zoom={12}
  markers={issueMarkers}
  onMarkerClick={handleMarkerClick}
  showClustering
  height="400px"
/>
```

### **MediaUpload Component**
```typescript
interface MediaUploadProps {
  onFilesAdd: (files: File[]) => void;
  onFileRemove: (index: number) => void;
  maxFiles?: number;
  maxSize?: number; // in bytes
  acceptedTypes: string[];
  showPreview?: boolean;
  dragDropText?: string;
  browseText?: string;
  className?: string;
}

// Usage from wireframes
<MediaUpload
  onFilesAdd={handleFilesAdd}
  onFileRemove={handleFileRemove}
  maxFiles={5}
  maxSize={10 * 1024 * 1024} // 10MB
  acceptedTypes={['image/*', 'video/*']}
  showPreview
  dragDropText="Drag photos here or click to browse"
/>
```

### **StatusTimeline Component**
```typescript
interface StatusTimelineProps {
  events: TimelineEvent[];
  currentStatus: IssueStatus;
  orientation?: 'vertical' | 'horizontal';
  showTimestamps?: boolean;
  showUsers?: boolean;
  className?: string;
}

interface TimelineEvent {
  id: string;
  status: IssueStatus;
  title: string;
  description?: string;
  timestamp: Date;
  user?: User;
  isCompleted: boolean;
  isCurrent: boolean;
}

// Usage from wireframes
<StatusTimeline
  events={issueEvents}
  currentStatus="in-progress"
  orientation="vertical"
  showTimestamps
  showUsers
/>
```

### **AnimatedCounter Component**
```typescript
interface AnimatedCounterProps {
  value: number;
  duration?: number;
  format?: (value: number) => string;
  trigger?: 'viewport' | 'mount' | 'manual';
  onComplete?: () => void;
  className?: string;
}

// Usage from wireframes - Statistics Cards
<AnimatedCounter
  value={12847}
  duration={2000}
  format={(n) => n.toLocaleString()}
  trigger="viewport"
/>
```

---

## 📊 Data Display Components

### **DataTable Component**
```typescript
interface DataTableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  pagination?: PaginationConfig;
  sorting?: SortingConfig;
  filtering?: FilteringConfig;
  selection?: SelectionConfig;
  onRowClick?: (row: T) => void;
  className?: string;
}

interface TableColumn<T> {
  key: keyof T;
  title: string;
  render?: (value: any, row: T) => React.ReactNode;
  sortable?: boolean;
  filterable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

// Usage from wireframes - Authority Dashboard
<DataTable
  data={issues}
  columns={issueColumns}
  pagination={{ pageSize: 20 }}
  sorting={{ defaultSort: 'createdAt', defaultOrder: 'desc' }}
  selection={{ multiple: true }}
  onRowClick={handleIssueClick}
/>
```

### **Chart Component**
```typescript
interface ChartProps {
  type: 'bar' | 'line' | 'pie' | 'doughnut' | 'area';
  data: ChartData;
  options?: ChartOptions;
  responsive?: boolean;
  animated?: boolean;
  height?: number;
  className?: string;
}

// Usage from wireframes - Analytics
<Chart
  type="bar"
  data={issuesByCategory}
  options={{ responsive: true }}
  animated
  height={300}
/>
```

---

## 🎭 Pattern Components

### **SearchWithFilters Component**
```typescript
interface SearchWithFiltersProps {
  onSearch: (query: string) => void;
  onFilterChange: (filters: FilterState) => void;
  filters: FilterConfig[];
  placeholder?: string;
  showRecentSearches?: boolean;
  className?: string;
}

// Usage from wireframes - Public Discovery
<SearchWithFilters
  onSearch={handleSearch}
  onFilterChange={handleFilterChange}
  filters={issueFilters}
  placeholder="Search issues..."
  showRecentSearches
/>
```

### **LoadingState Component**
```typescript
interface LoadingStateProps {
  variant: 'spinner' | 'skeleton' | 'pulse' | 'dots';
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  fullScreen?: boolean;
  className?: string;
}

// Usage from wireframes
<LoadingState
  variant="skeleton"
  size="lg"
  text="Loading issues..."
/>
```

---

## ♿ Accessibility Implementation

### **Focus Management**
```typescript
// Custom hook for focus management
export const useFocusManagement = () => {
  const trapFocus = (container: HTMLElement) => {
    // Implementation for focus trapping in modals
  };
  
  const restoreFocus = (element: HTMLElement) => {
    // Implementation for focus restoration
  };
  
  return { trapFocus, restoreFocus };
};
```

### **ARIA Helpers**
```typescript
// Utility functions for accessibility
export const ariaHelpers = {
  announceToScreenReader: (message: string) => {
    // Live region announcements
  },
  
  generateId: (prefix: string) => {
    // Unique ID generation for ARIA relationships
  },
  
  getAriaLabel: (element: string, context?: string) => {
    // Consistent ARIA labeling
  },
};
```

---

## 🧪 Testing Strategy

### **Component Testing**
```typescript
// Testing utilities for components
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
  );
  
  return render(ui, { wrapper: Wrapper, ...options });
};

// Accessibility testing
export const testAccessibility = async (component: React.ReactElement) => {
  const { container } = renderWithProviders(component);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
};
```

This component architecture provides a solid foundation for implementing the CityPulse wireframes with modern React patterns, TypeScript safety, and comprehensive accessibility support.
