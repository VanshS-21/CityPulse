# CityPulse Issue Reporting Wireframe
## Multi-Step Wizard with Map Integration

*Inspired by award-winning form designs with progressive disclosure, real-time validation, and intuitive user flows*

---

## 🎯 Design Overview

### Inspiration Sources
- **Progressive Web Apps**: Step-by-step guided experiences
- **Modern Form Design**: Clean, accessible form patterns
- **Map Integration**: Seamless location selection
- **Media Upload**: Drag-and-drop with instant preview

### Design Principles
- **Progressive Disclosure**: One step at a time to reduce cognitive load
- **Visual Feedback**: Clear progress indication and validation
- **Contextual Help**: Inline guidance and tooltips
- **Error Prevention**: Real-time validation and helpful suggestions

---

## 📱 Layout Structure

### Desktop Layout (1200px+)
```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER: Logo | Navigation | User Avatar                         │
├─────────────────────────────────────────────────────────────────┤
│ PROGRESS INDICATOR                                              │
│ ● ─────── ○ ─────── ○ ─────── ○ ─────── ○                      │
│ Location  Category  Details   Media     Review                  │
├─────────────────────────────────────────────────────────────────┤
│ MAIN CONTENT AREA                                               │
│ ┌─────────────────────────────┐ ┌─────────────────────────────┐ │
│ │ FORM STEP CONTENT           │ │ INTERACTIVE MAP             │ │
│ │                             │ │                             │ │
│ │ Step 1: Location Selection  │ │ ┌─────────────────────────┐ │ │
│ │ ┌─────────────────────────┐ │ │ │ [Search Location]       │ │ │
│ │ │ Search Address          │ │ │ └─────────────────────────┘ │ │
│ │ │ [123 Main St, City...] │ │ │                             │ │
│ │ └─────────────────────────┘ │ │ ┌─────────────────────────┐ │ │
│ │                             │ │ │                         │ │ │
│ │ ┌─────────────────────────┐ │ │ │    GOOGLE MAPS          │ │ │
│ │ │ [📍] Use Current        │ │ │ │    with marker          │ │ │
│ │ │     Location            │ │ │ │                         │ │ │
│ │ └─────────────────────────┘ │ │ └─────────────────────────┘ │ │
│ │                             │ │                             │ │
│ │ Selected Location:          │ │ ┌─────────────────────────┐ │ │
│ │ 📍 123 Main Street         │ │ │ [🎯] GPS Location       │ │ │
│ │    Downtown, City          │ │ │ [🔍] Search Places      │ │ │
│ │                             │ │ └─────────────────────────┘ │ │
│ └─────────────────────────────┘ └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ NAVIGATION                                                      │
│ [← Back]                                    [Continue →]        │
└─────────────────────────────────────────────────────────────────┘
```

### Mobile Layout (320px-768px)
```
┌─────────────────────────────────┐
│ HEADER: [←] Issue Report        │
├─────────────────────────────────┤
│ PROGRESS BAR                    │
│ ████████░░░░░░░░░░░░░░░░░░░░     │
│ Step 1 of 5: Location           │
├─────────────────────────────────┤
│ STEP CONTENT (Full Width)       │
│ ┌─────────────────────────────┐ │
│ │ Where is the issue?         │ │
│ │                             │ │
│ │ ┌─────────────────────────┐ │ │
│ │ │ Search Address          │ │ │
│ │ │ [123 Main St...]        │ │ │
│ │ └─────────────────────────┘ │ │
│ │                             │ │
│ │ ┌─────────────────────────┐ │ │
│ │ │ [📍] Use GPS Location   │ │ │
│ │ └─────────────────────────┘ │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ MAP PREVIEW                     │
│ ┌─────────────────────────────┐ │
│ │                             │ │
│ │    MINI MAP VIEW            │ │
│ │    with selected marker     │ │
│ │                             │ │
│ └─────────────────────────────┘ │
│ [📍] 123 Main Street            │
│      Downtown, City             │
├─────────────────────────────────┤
│ ACTIONS                         │
│ [Back]              [Continue]  │
└─────────────────────────────────┘
```

---

## 🎨 Step-by-Step Components

### Step 1: Location Selection
```typescript
interface LocationStepProps {
  selectedLocation: Location | null
  onLocationSelect: (location: Location) => void
  onNext: () => void
}

interface Location {
  address: string
  coordinates: { lat: number; lng: number }
  placeId?: string
  city: string
  district?: string
}
```

**Visual Design:**
- **Search Input**: Autocomplete with Google Places API
- **GPS Button**: One-click current location detection
- **Map Integration**: Interactive Google Maps with marker
- **Location Display**: Clear address confirmation

**Interactive Features:**
- **Address Autocomplete**: Real-time suggestions
- **Map Click**: Click to place marker
- **GPS Detection**: Automatic location with permission
- **Validation**: Ensure location is within service area

### Step 2: Category Selection
```typescript
interface CategoryStepProps {
  categories: IssueCategory[]
  selectedCategory: string | null
  onCategorySelect: (categoryId: string) => void
}

interface IssueCategory {
  id: string
  name: string
  icon: string
  description: string
  color: string
  subcategories?: string[]
}
```

**Layout Design:**
```
┌─────────────────────────────────────────────────────────────────┐
│ What type of issue are you reporting?                           │
├─────────────────────────────────────────────────────────────────┤
│ CATEGORY GRID (3x3 Desktop, 2x4 Mobile)                        │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                            │
│ │ 🚧      │ │ 🚮      │ │ 💡      │                            │
│ │ Road    │ │ Waste   │ │ Street  │                            │
│ │ Issues  │ │ Mgmt    │ │ Lights  │                            │
│ └─────────┘ └─────────┘ └─────────┘                            │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                            │
│ │ 🌳      │ │ 🏢      │ │ 🚰      │                            │
│ │ Parks   │ │ Building│ │ Water   │                            │
│ │ & Trees │ │ Issues  │ │ Issues  │                            │
│ └─────────┘ └─────────┘ └─────────┘                            │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                            │
│ │ 🚦      │ │ 🔊      │ │ ❓      │                            │
│ │ Traffic │ │ Noise   │ │ Other   │                            │
│ │ Signals │ │ Issues  │ │         │                            │
│ └─────────┘ └─────────┘ └─────────┘                            │
├─────────────────────────────────────────────────────────────────┤
│ SUBCATEGORY (if applicable)                                     │
│ Selected: Road Issues                                           │
│ ○ Pothole  ○ Crack  ○ Debris  ○ Construction                  │
└─────────────────────────────────────────────────────────────────┘
```

**Interactive States:**
- **Hover**: Card lift with shadow increase
- **Selected**: Border highlight and background tint
- **Subcategory**: Expand to show specific options
- **Validation**: Ensure category selection before proceeding

### Step 3: Issue Details
```typescript
interface DetailsStepProps {
  formData: {
    title: string
    description: string
    severity: 'low' | 'medium' | 'high' | 'urgent'
    isPublic: boolean
  }
  onChange: (field: string, value: any) => void
}
```

**Form Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Tell us more about the issue                                    │
├─────────────────────────────────────────────────────────────────┤
│ ISSUE TITLE                                                     │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Brief title (e.g., "Large pothole on Main Street")         │ │
│ │ [                                                         ] │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ DESCRIPTION                                                     │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Describe the issue in detail...                             │ │
│ │ [                                                         ] │ │
│ │ [                                                         ] │ │
│ │ [                                                         ] │ │
│ │ [                                                         ] │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ SEVERITY LEVEL                                                  │
│ ○ Low      ○ Medium      ● High      ○ Urgent                  │
│ Minor      Moderate      Significant  Immediate                │
│ issue      concern       problem      attention                │
├─────────────────────────────────────────────────────────────────┤
│ VISIBILITY                                                      │
│ ☑ Make this report public (visible to other citizens)          │
│ ☐ Keep this report private (only visible to authorities)       │
└─────────────────────────────────────────────────────────────────┘
```

**Validation Rules:**
- **Title**: 10-100 characters, required
- **Description**: 20-1000 characters, required
- **Severity**: Must select one option
- **Character Counters**: Real-time feedback

### Step 4: Media Upload
```typescript
interface MediaStepProps {
  files: File[]
  onFilesAdd: (files: File[]) => void
  onFileRemove: (index: number) => void
  maxFiles: number
  maxSize: number
}
```

**Upload Interface:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Add photos or videos (optional but recommended)                 │
├─────────────────────────────────────────────────────────────────┤
│ DRAG & DROP AREA                                                │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                                                             │ │
│ │                    📷                                       │ │
│ │                                                             │ │
│ │         Drag photos here or click to browse                 │ │
│ │                                                             │ │
│ │         Supports: JPG, PNG, MP4 (max 10MB each)           │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ UPLOADED FILES                                                  │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                            │
│ │ [IMG]   │ │ [IMG]   │ │ [VID]   │                            │
│ │ photo1  │ │ photo2  │ │ video1  │                            │
│ │ 2.3MB   │ │ 1.8MB   │ │ 8.1MB   │                            │
│ │   [×]   │ │   [×]   │ │   [×]   │                            │
│ └─────────┘ └─────────┘ └─────────┘                            │
├─────────────────────────────────────────────────────────────────┤
│ CAMERA CAPTURE (Mobile)                                         │
│ [📷 Take Photo]  [🎥 Record Video]                             │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Drag & Drop**: Visual feedback during drag operations
- **File Preview**: Thumbnail generation for images/videos
- **Progress Indicators**: Upload progress for each file
- **Error Handling**: File size, type, and count validation
- **Mobile Camera**: Direct camera access on mobile devices

### Step 5: Review & Submit
```typescript
interface ReviewStepProps {
  reportData: IssueReport
  onSubmit: () => Promise<void>
  onEdit: (step: number) => void
}
```

**Review Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Review your report before submitting                            │
├─────────────────────────────────────────────────────────────────┤
│ LOCATION                                               [Edit]   │
│ 📍 123 Main Street, Downtown, City                              │
├─────────────────────────────────────────────────────────────────┤
│ CATEGORY                                               [Edit]   │
│ 🚧 Road Issues > Pothole                                       │
├─────────────────────────────────────────────────────────────────┤
│ DETAILS                                                [Edit]   │
│ Title: Large pothole on Main Street                             │
│ Severity: High                                                  │
│ Public: Yes                                                     │
│                                                                 │
│ Description: There's a large pothole that has been growing...   │
├─────────────────────────────────────────────────────────────────┤
│ MEDIA (3 files)                                        [Edit]   │
│ [📷] [📷] [🎥]                                                  │
├─────────────────────────────────────────────────────────────────┤
│ SUBMISSION                                                      │
│ ☑ I confirm this information is accurate                       │
│ ☑ I agree to the Terms of Service                              │
│                                                                 │
│ [Submit Report]                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎭 Animation & Interaction Specifications

### Step Transitions
```css
/* Step content slide animation */
@keyframes stepSlide {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Progress indicator animation */
@keyframes progressFill {
  from { width: 0%; }
  to { width: var(--progress-width); }
}
```

### Micro-interactions
- **Category Cards**: Hover lift and selection highlight
- **File Upload**: Drag feedback and upload progress
- **Form Validation**: Real-time error/success indicators
- **Map Interactions**: Smooth marker placement and zoom

### Loading States
- **GPS Detection**: Spinner with location icon
- **File Upload**: Progress bars with percentage
- **Form Submission**: Button loading state with success feedback

---

## 📊 Success Metrics

### User Experience
- **Completion Rate**: > 80% of started reports
- **Time to Complete**: < 5 minutes average
- **Error Rate**: < 5% validation errors
- **User Satisfaction**: > 4.5/5 rating

### Technical Performance
- **Step Load Time**: < 500ms per step
- **File Upload Speed**: Progress feedback within 100ms
- **Map Performance**: < 2s initial load
- **Mobile Performance**: 60fps animations

This issue reporting wireframe creates an intuitive, step-by-step experience that guides users through the reporting process while maintaining engagement and reducing abandonment rates.