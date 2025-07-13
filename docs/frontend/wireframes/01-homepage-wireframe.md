# CityPulse Homepage Wireframe
## Award-Winning Design Patterns Integration

*Based on Awwwards 2024-2025 winning designs with glassmorphism, micro-interactions, and modern data visualization*

---

## 🎯 Design Overview

### Inspiration Sources
- **Electra Filmworks** (SOTD Jul 2025): Cinematic hero sections with animated backgrounds
- **Background Remover** (SOTD Jul 2025): Clean, functional UI with smooth interactions
- **The ADHD Experience** (SOTD Jul 2025): Accessible design with clear information hierarchy
- **Modern Animation Trends**: Scroll-triggered animations, parallax effects, glassmorphism

### Design Principles
- **Urban Intelligence**: Tech-forward aesthetic with city-inspired elements
- **Glassmorphism**: Translucent cards with backdrop blur effects
- **Micro-interactions**: Subtle animations that enhance user experience
- **Data-Driven**: Clean metrics presentation with animated counters
- **Accessibility-First**: WCAG 2.1 AA compliance built into every element

---

## 📱 Layout Structure

### Desktop Layout (1024px+)
```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER: Logo | Navigation | User Actions                        │
├─────────────────────────────────────────────────────────────────┤
│ HERO SECTION                                                    │
│ ┌─────────────────────┐ ┌─────────────────────────────────────┐ │
│ │ Animated City       │ │ Value Proposition                   │ │
│ │ Visualization       │ │ • Headline with gradient text       │ │
│ │ • SVG skyline       │ │ • Subheading with urban context     │ │
│ │ • Parallax layers   │ │ • Primary CTA button                │ │
│ │ • Floating elements │ │ • Secondary CTA button              │ │
│ └─────────────────────┘ └─────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ STATISTICS SECTION (Glassmorphism Cards)                       │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                │
│ │ Issues  │ │ Resolved│ │ Active  │ │ Response│                │
│ │ Reported│ │ Today   │ │ Users   │ │ Time    │                │
│ │ 12,847  │ │ 234     │ │ 5,692   │ │ 2.3hrs  │                │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘                │
├─────────────────────────────────────────────────────────────────┤
│ FEATURES SECTION                                                │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Three-column grid with feature cards                       │ │
│ │ • Icon + Title + Description + Learn More                  │ │
│ │ • Hover effects with subtle lift                           │ │
│ │ • Progressive disclosure on interaction                     │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ ROLE-BASED CTA SECTION                                         │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ "Choose Your Role" with three distinct paths               │ │
│ │ [Citizen] [Authority] [Administrator]                      │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ FOOTER: Links | Legal | Contact | Social                       │
└─────────────────────────────────────────────────────────────────┘
```

### Mobile Layout (320px-768px)
```
┌─────────────────────────────────┐
│ HEADER: Logo | Hamburger Menu   │
├─────────────────────────────────┤
│ HERO SECTION (Stacked)          │
│ ┌─────────────────────────────┐ │
│ │ Animated City Visual        │ │
│ │ (Simplified for mobile)     │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ Value Proposition           │ │
│ │ • Large headline            │ │
│ │ • Concise subheading        │ │
│ │ • Single primary CTA        │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ STATISTICS (2x2 Grid)           │
│ ┌─────────┐ ┌─────────┐         │
│ │ Issues  │ │ Resolved│         │
│ │ 12,847  │ │ 234     │         │
│ └─────────┘ └─────────┘         │
│ ┌─────────┐ ┌─────────┐         │
│ │ Users   │ │ Response│         │
│ │ 5,692   │ │ 2.3hrs  │         │
│ └─────────┘ └─────────┘         │
├─────────────────────────────────┤
│ FEATURES (Single Column)        │
│ ┌─────────────────────────────┐ │
│ │ Feature Card 1              │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ Feature Card 2              │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ Feature Card 3              │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ ROLE CTA (Stacked Buttons)      │
│ ┌─────────────────────────────┐ │
│ │ [Citizen]                   │ │
│ │ [Authority]                 │ │
│ │ [Administrator]             │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ FOOTER (Collapsed)              │
└─────────────────────────────────┘
```

---

## 🎨 Component Specifications

### Header Component
```typescript
interface HeaderProps {
  isAuthenticated: boolean
  userRole?: 'citizen' | 'authority' | 'admin'
  onMenuToggle: () => void
}
```

**Visual Design:**
- **Background**: Glassmorphism with backdrop-filter: blur(10px)
- **Height**: 80px desktop, 64px mobile
- **Logo**: SVG with urban pulse animation
- **Navigation**: Horizontal menu with hover underline animations
- **User Actions**: Login/Register buttons or user avatar dropdown

**Interactive States:**
- **Scroll Behavior**: Header becomes more opaque on scroll
- **Mobile Menu**: Slide-in overlay with staggered animation
- **Hover Effects**: Subtle glow on interactive elements

**Responsive Behavior:**
- Desktop: Full horizontal navigation
- Tablet: Condensed navigation with some items in dropdown
- Mobile: Hamburger menu with full-screen overlay

### Hero Section Component
```typescript
interface HeroSectionProps {
  onPrimaryCTA: () => void
  onSecondaryCTA: () => void
  animationEnabled: boolean
}
```

**Visual Design:**
- **Background**: Gradient mesh with animated city skyline SVG
- **Typography**: 
  - H1: 4rem desktop, 2.5rem mobile with gradient text
  - Subheading: 1.25rem with urban context
- **CTAs**: Primary (solid) and secondary (outline) buttons
- **Animation**: Parallax city elements, floating particles

**Interactive States:**
- **Parallax**: City elements move at different speeds on scroll
- **Button Hover**: Lift effect with shadow increase
- **Loading States**: Skeleton animation while content loads

**Accessibility:**
- **Reduced Motion**: Respects prefers-reduced-motion
- **Focus Management**: Clear focus indicators
- **Screen Reader**: Proper heading hierarchy and alt text

### Statistics Cards Component
```typescript
interface StatisticsCardProps {
  title: string
  value: number
  unit?: string
  trend?: 'up' | 'down' | 'neutral'
  icon: React.ReactNode
}
```

**Visual Design:**
- **Card Style**: Glassmorphism with backdrop-filter: blur(20px)
- **Background**: rgba(255, 255, 255, 0.1) with subtle border
- **Shadow**: 0 8px 32px rgba(0, 0, 0, 0.1)
- **Border Radius**: 16px for modern appearance
- **Typography**: Large numbers with smaller unit text

**Animation Specifications:**
- **Counter Animation**: Easing function with 2-second duration
- **Trigger**: Intersection Observer when 50% visible
- **Hover Effect**: Scale(1.05) with increased backdrop blur
- **Loading State**: Skeleton with shimmer effect

**Responsive Behavior:**
- Desktop: 1x4 horizontal grid
- Tablet: 2x2 grid
- Mobile: 2x2 grid with smaller cards

### Feature Cards Component
```typescript
interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  description: string
  learnMoreUrl: string
  imageUrl?: string
}
```

**Visual Design:**
- **Layout**: Icon + Title + Description + CTA
- **Background**: Subtle gradient with glassmorphism
- **Icon**: 48px with urban theme colors
- **Typography**: Clear hierarchy with readable contrast

**Interactive States:**
- **Hover**: Lift animation with increased shadow
- **Focus**: Clear outline with brand color
- **Active**: Slight scale down for tactile feedback

**Animation Timing:**
- **Hover Transition**: 200ms ease-out
- **Stagger Animation**: 100ms delay between cards on load
- **Scroll Reveal**: Fade up animation on viewport entry

---

## 🎭 Animation Specifications

### Scroll-Triggered Animations
```css
/* Hero parallax layers */
.hero-background { transform: translateY(scrollY * 0.5); }
.hero-midground { transform: translateY(scrollY * 0.3); }
.hero-foreground { transform: translateY(scrollY * 0.1); }

/* Statistics counter animation */
@keyframes countUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Feature cards stagger */
.feature-card:nth-child(1) { animation-delay: 0ms; }
.feature-card:nth-child(2) { animation-delay: 100ms; }
.feature-card:nth-child(3) { animation-delay: 200ms; }
```

### Micro-interactions
- **Button Hover**: Scale(1.02) + shadow increase
- **Card Hover**: translateY(-4px) + shadow enhancement
- **Icon Animations**: Subtle rotation or pulse on hover
- **Loading States**: Skeleton shimmer with 1.5s duration

### Performance Considerations
- **GPU Acceleration**: transform3d for smooth animations
- **Intersection Observer**: Lazy load animations
- **Reduced Motion**: Respect user preferences
- **Frame Rate**: Target 60fps for all animations

---

## 🔧 Technical Implementation

### Component Architecture
```typescript
// Homepage component structure
const Homepage = () => {
  return (
    <div className="homepage">
      <Header />
      <HeroSection />
      <StatisticsSection />
      <FeaturesSection />
      <RoleBasedCTASection />
      <Footer />
    </div>
  )
}
```

### Styling Approach
- **Tailwind CSS**: Utility-first with custom components
- **CSS Custom Properties**: Dynamic theming support
- **Glassmorphism Utilities**: Reusable backdrop-filter classes
- **Animation Classes**: Consistent motion language

### Performance Optimization
- **Code Splitting**: Lazy load non-critical components
- **Image Optimization**: Next.js Image with WebP/AVIF
- **Bundle Analysis**: Monitor component bundle sizes
- **Critical CSS**: Inline above-the-fold styles

---

## ✅ Accessibility Checklist

### WCAG 2.1 AA Compliance
- [ ] Color contrast ratio ≥ 4.5:1 for normal text
- [ ] Color contrast ratio ≥ 3:1 for large text
- [ ] Keyboard navigation for all interactive elements
- [ ] Screen reader compatibility with proper ARIA labels
- [ ] Focus indicators visible and consistent
- [ ] Reduced motion support for animations
- [ ] Semantic HTML structure with proper headings
- [ ] Alternative text for all images and icons

### Testing Strategy
- [ ] Automated testing with jest-axe
- [ ] Manual keyboard navigation testing
- [ ] Screen reader testing (NVDA, JAWS, VoiceOver)
- [ ] Color blindness simulation testing
- [ ] Mobile accessibility testing

---

## 📊 Success Metrics

### User Experience Metrics
- **Time to Interactive**: < 3 seconds
- **First Contentful Paint**: < 1.5 seconds
- **Cumulative Layout Shift**: < 0.1
- **Bounce Rate**: < 40%
- **Conversion Rate**: > 15% (role selection)

### Technical Metrics
- **Lighthouse Score**: > 90 for all categories
- **Bundle Size**: < 200KB initial load
- **Animation Performance**: 60fps maintained
- **Accessibility Score**: 100% automated testing

This homepage wireframe integrates award-winning design patterns with modern web standards, creating an engaging entry point that effectively communicates CityPulse's value proposition while maintaining excellent performance and accessibility.
