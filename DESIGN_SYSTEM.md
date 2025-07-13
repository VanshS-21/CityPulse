# CityPulse Design System

## 🎨 Overview

The CityPulse Design System is a comprehensive collection of reusable components, design tokens, and
guidelines that ensures consistency and efficiency across the entire urban intelligence platform.

## 🎯 Design Principles

### **Trust & Reliability**- Clear visual hierarchy

-     Consistent interaction patterns
-     Accessible design standards
-     Professional appearance

### **Data Clarity**- Clean information architecture

-     Readable typography
-     Meaningful use of color
-     Efficient data visualization

### **Urban Intelligence**- Modern, tech-forward aesthetic

-     City-inspired color palette
-     Scalable components
-     Responsive design

## 🏗️ Architecture

### **Atomic Design Structure**```text

Design System ├── Tokens/ # Design tokens (colors, spacing, typography) ├── Base/ # Foundational
components (Button, Input, Card) ├── Composite/ # Complex components (Forms, Navigation) ├──
Patterns/ # Common UI patterns and templates └── Guidelines/ # Usage guidelines and best practices

````text

## 🎨 Design Tokens

### **Color Palette**#### Primary Colors

```scss

primary-50:  #eff6ff
primary-100: #dbeafe
primary-200: #bfdbfe
primary-300: #93c5fd
primary-400: #60a5fa
primary-500: #3b82f6  // Main brand color
primary-600: #2563eb
primary-700: #1d4ed8
primary-800: #1e40af
primary-900: #1e3a8a
primary-950: #172554

```text

### Semantic Colors

-   **Success**: Green palette for positive actions and states
-     **Warning**: Amber palette for caution and attention
-     **Error**: Red palette for errors and destructive actions
-     **Info**: Blue palette for informational content

#### Urban Theme Colors

-     **Sky**: `#0ea5e9`- Open spaces and clarity
-     **Ocean**:`#0284c7`- Depth and reliability
-     **Forest**:`#059669`- Growth and sustainability
-     **Sunset**:`#ea580c`- Energy and warmth
-     **Night**:`#1e293b`- Professional and elegant
-     **Dawn**:`#fbbf24`- Innovation and opportunity

### **Typography Scale**#### Font Families

-   **Sans**: Inter (primary), system fonts
-     **Mono**: JetBrains Mono, Fira Code (code/data)
-     **Display**: Inter (headings)

#### Font Sizes```scss

text-xs:   0.75rem   (12px)
text-sm:   0.875rem  (14px)
text-base: 1rem      (16px)
text-lg:   1.125rem  (18px)
text-xl:   1.25rem   (20px)
text-2xl:  1.5rem    (24px)
text-3xl:  1.875rem  (30px)
text-4xl:  2.25rem   (36px)
text-5xl:  3rem      (48px)
```text

### **Spacing Scale**Based on 0.25rem (4px) increments

```scss
1:  0.25rem   (4px)
2:  0.5rem    (8px)
3:  0.75rem   (12px)
4:  1rem      (16px)
5:  1.25rem   (20px)
6:  1.5rem    (24px)
8:  2rem      (32px)
10: 2.5rem    (40px)
12: 3rem      (48px)
16: 4rem      (64px)
20: 5rem      (80px)
```text

### **Border Radius**```scss

sm:  0.125rem  (2px)
md:  0.375rem  (6px)
lg:  0.5rem    (8px)
xl:  0.75rem   (12px)
2xl: 1rem      (16px)
3xl: 1.5rem    (24px)

```text

### **Shadows**```scss

soft:     Subtle shadow for cards
medium:   Standard elevation
hard:     Strong emphasis
glow:     Interactive elements
glow-lg:  High emphasis
```text

## 🧩 Base Components

### **Button**#### Variants

-     `primary`- Main brand color, primary actions
-   `secondary`- Subtle background, secondary actions
-   `success`- Green, positive actions
-   `warning`- Amber, cautionary actions
-   `destructive`- Red, dangerous actions
-   `outline`- Bordered style
-   `ghost`- Minimal style
-   `link`- Link appearance
-   `urban`- Urban theme variant

### Sizes

-   `xs`- 24px height, compact spaces
-   `sm`- 32px height, tight layouts
-   `md`- 40px height, standard use
-   `lg`- 44px height, prominent actions
-   `xl`- 48px height, hero actions

#### Usage```tsx

<Button variant="primary" size="md">
  Primary Action
</Button>

<Button variant="outline" leftIcon={<PlusIcon />}>
  Add Item
</Button>

<Button variant="ghost" loading>
  Loading...
</Button>

```text

### **Input**#### Variants 2

-     `default`- Standard input style
-   `success`- Success state
-   `warning`- Warning state
-   `error`- Error state

#### Features

-     Label support
-     Helper text
-     Error messages
-     Left/right icons
-     Left/right addons

#### Usage 2```tsx

<Input
  label="Email"
  placeholder="Enter your email"
  helperText="We'll never share your email"
/>

<Input
  variant="error"
  errorMessage="This field is required"
  leftIcon={<EmailIcon />}
/>
```text

### **Card**#### Variants 3

-     `default`- Standard card
-   `elevated`- Increased shadow
-   `outlined`- Emphasized border
-   `filled`- Background fill
-   `urban`- Urban theme styling

#### Anatomy

-   `Card`- Container
-   `CardHeader`- Header section
-   `CardTitle`- Title text
-   `CardDescription`- Subtitle text
-   `CardContent`- Main content
-   `CardFooter`- Footer actions

#### Usage 3```tsx

<Card variant="elevated">
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>

```text

### **Badge**#### Variants 4

-     `default`- Primary badge
-   `secondary`- Secondary style
-   `success`- Success indicator
-   `warning`- Warning indicator
-   `error`- Error indicator
-   `outline`- Outlined style
-   `urban`- Urban theme

#### Features 2

-     Icon support
-     Removable badges
-     Multiple sizes

#### Usage 4```tsx

<Badge variant="success">Active</Badge>
<Badge variant="warning" icon={<WarningIcon />}>
  Warning
</Badge>
<Badge removable onRemove={() => {}}>
  Removable
</Badge>
```text

## 📐 Layout System

### **Responsive Breakpoints**```scss

sm:  640px   // Small devices
md:  768px   // Medium devices
lg:  1024px  // Large devices
xl:  1280px  // Extra large devices
2xl: 1536px  // 2X large devices

```text

### **Container Sizes**-  Responsive containers with proper margins

-     Max-width constraints for readability
-     Consistent padding across breakpoints

## 🎭 Animation System

### **Transitions**-  `fade-in`- 200ms fade in

-   `fade-out`- 200ms fade out
-   `slide-in`- 300ms slide in from top
-   `slide-out`- 300ms slide out to top
-   `bounce-in`- 500ms bounce entrance
-   `scale-in`- 200ms scale entrance

### **Timing Functions**-`ease`- Standard easing

-   `ease-in`- Acceleration
-   `ease-out`- Deceleration
-   `ease-in-out` - Acceleration then deceleration

## 🔧 Implementation

### **Using Components**```tsx

import { Button, Card, Input, Badge } from '@/components/ui'

function ExampleComponent() {
  return (
    <Card variant="elevated">
      <CardHeader>
        <CardTitle>User Profile</CardTitle>
        <Badge variant="success">Active</Badge>
      </CardHeader>
      <CardContent>
        <Input label="Name" placeholder="Enter your name" />
      </CardContent>
      <CardFooter>
        <Button variant="primary">Save Changes</Button>
      </CardFooter>
    </Card>
  )
}
```text

### **Using Design Tokens**```tsx

import { colors, spacing, typography } from '@/styles/tokens'

// In styled components or custom CSS
const customStyles = {
  color: colors.primary[500],
  padding: spacing[4],
  fontSize: typography.fontSize.lg[0],
}

```text

### **Using Utilities**```tsx

import { cn } from '@/lib/utils'

function Component({ className, variant }) {
  return (
    <div className={cn(
      'base-classes',
      {
        'variant-classes': variant === 'special',
      },
      className
    )}>
      Content
    </div>
  )
}
```text

## 📝 Best Practices

### **Component Usage**1.**Use design system components first**before creating custom ones

1.  **Follow variant patterns**for consistent behavior
1.  **Compose components**instead of modifying base styles
1.  **Test accessibility**with keyboard navigation and screen readers

### **Color Usage**1.**Use semantic colors**for status and actions

1.  **Maintain contrast ratios**for accessibility (WCAG AA: 4.5:1)
1.  **Test in different lighting**conditions
1.  **Consider color blindness**when using color alone for meaning

### **Typography**1.**Use consistent scales**from the typography system

1.  **Maintain readable line heights**(1.4-1.6 for body text)
1.  **Limit font weights**to 3-4 per project
1.  **Test readability**at different sizes

### **Spacing**1.**Use the spacing scale**instead of arbitrary values

1.  **Be consistent**with margins and padding
1.  **Create rhythm**with consistent vertical spacing
1.  **Use relative units**for scalability

## 🧪 Testing

### **Component Testing**-  Unit tests for component behavior

-     Visual regression tests for styling
-     Accessibility tests with axe-core
-     Interactive tests with user events

### **Design System Validation**-  Token usage validation

-     Component variant testing
-     Cross-browser compatibility
-     Mobile responsiveness

## 📚 Resources

### **Tools Used**-**Tailwind CSS**- Utility-first CSS framework

-   **Class Variance Authority**- Component variant management
-   **Radix UI**- Accessible component primitives
-   **Lucide React**- Icon system
-   **TypeScript**- Type safety

### **Inspiration**-  Material Design 3

-     Apple Human Interface Guidelines
-     Ant Design
-     Chakra UI
-     Tailwind UI

-   *CityPulse Design System** - Building consistent, accessible, and beautiful urban intelligence interfaces 🏙️
````
