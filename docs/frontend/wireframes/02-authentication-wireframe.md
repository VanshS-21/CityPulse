# CityPulse Authentication Flow Wireframe
## Modern Modal-Based Authentication with Role Selection

*Inspired by award-winning authentication patterns with glassmorphism, smooth transitions, and accessibility-first design*

---

## 🎯 Design Overview

### Inspiration Sources
- **Modern Authentication Trends**: Modal-based flows with backdrop blur
- **Role-Based Access**: Clear visual distinction between user types
- **Micro-interactions**: Smooth transitions and feedback animations
- **Accessibility**: Screen reader friendly with proper focus management

### Design Principles
- **Seamless Experience**: Non-disruptive modal overlay
- **Clear Role Distinction**: Visual cards for different user types
- **Progressive Disclosure**: Step-by-step information gathering
- **Trust Building**: Professional appearance with security indicators

---

## 📱 Layout Structure

### Desktop Modal (600px width)
```
┌─────────────────────────────────────────────────────────────────┐
│ BACKDROP (Glassmorphism blur)                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ MODAL HEADER                                            │   │
│   │ ┌─────────────────────┐ ┌─────────────────────────────┐ │   │
│   │ │ [Login] (Active)    │ │ [Register]                  │ │   │
│   │ └─────────────────────┘ └─────────────────────────────┘ │   │
│   │                                                 [×]     │   │
│   ├─────────────────────────────────────────────────────────┤   │
│   │ ROLE SELECTION (Register Only)                          │   │
│   │ ┌─────────┐ ┌─────────┐ ┌─────────┐                    │   │
│   │ │ CITIZEN │ │AUTHORITY│ │  ADMIN  │                    │   │
│   │ │ 👤      │ │ 🏛️      │ │ ⚙️      │                    │   │
│   │ │ Report  │ │ Manage  │ │ System  │                    │   │
│   │ │ Issues  │ │ Issues  │ │ Admin   │                    │   │
│   │ └─────────┘ └─────────┘ └─────────┘                    │   │
│   ├─────────────────────────────────────────────────────────┤   │
│   │ FORM FIELDS                                             │   │
│   │ ┌─────────────────────────────────────────────────────┐ │   │
│   │ │ Email Address                                       │ │   │
│   │ │ [email@example.com                               ] │ │   │
│   │ └─────────────────────────────────────────────────────┘ │   │
│   │ ┌─────────────────────────────────────────────────────┐ │   │
│   │ │ Password                                            │ │   │
│   │ │ [••••••••••••••••••••••••••••••••••••••••••••••] │ │   │
│   │ └─────────────────────────────────────────────────────┘ │   │
│   │ ┌─────────────────────────────────────────────────────┐ │   │
│   │ │ Confirm Password (Register Only)                    │ │   │
│   │ │ [••••••••••••••••••••••••••••••••••••••••••••••] │ │   │
│   │ └─────────────────────────────────────────────────────┘ │   │
│   ├─────────────────────────────────────────────────────────┤   │
│   │ SOCIAL AUTHENTICATION                                   │   │
│   │ ┌─────────────────────┐ ┌─────────────────────────────┐ │   │
│   │ │ [G] Google          │ │ [f] Facebook                │ │   │
│   │ └─────────────────────┘ └─────────────────────────────┘ │   │
│   ├─────────────────────────────────────────────────────────┤   │
│   │ ACTIONS                                                 │   │
│   │ ┌─────────────────────────────────────────────────────┐ │   │
│   │ │ [Sign In] / [Create Account]                        │ │   │
│   │ └─────────────────────────────────────────────────────┘ │   │
│   │ Forgot Password? | Terms & Privacy                      │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Mobile Modal (Full Screen)
```
┌─────────────────────────────────┐
│ HEADER                          │
│ [×] CityPulse Authentication    │
├─────────────────────────────────┤
│ TAB NAVIGATION                  │
│ [Login] [Register]              │
├─────────────────────────────────┤
│ ROLE SELECTION (Stacked)        │
│ ┌─────────────────────────────┐ │
│ │ 👤 CITIZEN                  │ │
│ │ Report community issues     │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ 🏛️ AUTHORITY                │ │
│ │ Manage and resolve issues   │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ ⚙️ ADMINISTRATOR            │ │
│ │ System administration       │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ FORM FIELDS                     │
│ ┌─────────────────────────────┐ │
│ │ Email Address               │ │
│ │ [email@example.com        ] │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ Password                    │ │
│ │ [•••••••••••••••••••••••••] │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ SOCIAL AUTH (Stacked)           │
│ ┌─────────────────────────────┐ │
│ │ [G] Continue with Google    │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ [f] Continue with Facebook  │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ PRIMARY ACTION                  │
│ ┌─────────────────────────────┐ │
│ │ [Sign In] / [Create Account]│ │
│ └─────────────────────────────┘ │
│ Forgot Password?                │
│ Terms & Privacy                 │
└─────────────────────────────────┘
```

---

## 🎨 Component Specifications

### Authentication Modal Component
```typescript
interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  defaultMode: 'login' | 'register'
  onSuccess: (user: User) => void
}

interface AuthState {
  mode: 'login' | 'register'
  selectedRole: 'citizen' | 'authority' | 'admin' | null
  formData: {
    email: string
    password: string
    confirmPassword?: string
  }
  loading: boolean
  errors: Record<string, string>
}
```

**Visual Design:**
- **Modal Background**: backdrop-filter: blur(20px) with rgba overlay
- **Modal Container**: Glassmorphism card with rounded corners
- **Dimensions**: 600px width desktop, full-screen mobile
- **Animation**: Scale and fade-in entrance, backdrop blur transition

**Interactive States:**
- **Tab Switching**: Smooth transition between Login/Register
- **Role Selection**: Visual feedback with selected state
- **Form Validation**: Real-time inline validation
- **Loading States**: Button spinner and disabled state

### Role Selection Cards Component
```typescript
interface RoleCardProps {
  role: 'citizen' | 'authority' | 'admin'
  selected: boolean
  onSelect: (role: string) => void
  disabled?: boolean
}
```

**Visual Design:**
- **Card Style**: Glassmorphism with hover and selected states
- **Icon**: Large emoji or SVG icon (48px)
- **Typography**: Role title + description
- **Selection State**: Border highlight and background change

**Role Definitions:**
```typescript
const roles = {
  citizen: {
    icon: '👤',
    title: 'Citizen',
    description: 'Report community issues and track progress',
    color: 'blue'
  },
  authority: {
    icon: '🏛️',
    title: 'Authority',
    description: 'Manage and resolve reported issues',
    color: 'green'
  },
  admin: {
    icon: '⚙️',
    title: 'Administrator',
    description: 'System administration and user management',
    color: 'purple'
  }
}
```

**Interactive States:**
- **Hover**: Subtle lift and glow effect
- **Selected**: Border highlight and background tint
- **Focus**: Clear outline for keyboard navigation
- **Disabled**: Reduced opacity and no interactions

### Form Fields Component
```typescript
interface FormFieldProps {
  label: string
  type: 'email' | 'password' | 'text'
  value: string
  onChange: (value: string) => void
  error?: string
  required?: boolean
  autoComplete?: string
}
```

**Visual Design:**
- **Input Style**: Glassmorphism with subtle border
- **Label**: Floating label animation
- **Error State**: Red border and error message
- **Success State**: Green border for valid inputs

**Validation Rules:**
- **Email**: Valid email format with domain check
- **Password**: Minimum 8 characters, mixed case, numbers
- **Confirm Password**: Must match original password
- **Real-time Validation**: Debounced validation on input

### Social Authentication Component
```typescript
interface SocialAuthProps {
  providers: ('google' | 'facebook' | 'github')[]
  onSocialAuth: (provider: string) => Promise<void>
  loading?: string // Currently loading provider
}
```

**Visual Design:**
- **Button Style**: Provider-specific colors and icons
- **Layout**: Side-by-side desktop, stacked mobile
- **Loading State**: Spinner in button during authentication

**Security Features:**
- **OAuth 2.0**: Secure third-party authentication
- **CSRF Protection**: State parameter validation
- **Scope Limitation**: Minimal required permissions

---

## 🎭 Animation Specifications

### Modal Animations
```css
/* Modal entrance */
@keyframes modalEnter {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Backdrop blur transition */
@keyframes backdropBlur {
  from { backdrop-filter: blur(0px); }
  to { backdrop-filter: blur(20px); }
}

/* Tab switching */
@keyframes tabSwitch {
  from { opacity: 0; transform: translateX(10px); }
  to { opacity: 1; transform: translateX(0); }
}
```

### Micro-interactions
- **Role Card Hover**: Scale(1.02) + shadow increase
- **Button Hover**: Background color transition
- **Input Focus**: Border color and shadow animation
- **Error Shake**: Subtle shake animation for validation errors

### Loading States
- **Button Loading**: Spinner animation with disabled state
- **Form Submission**: Overlay with loading indicator
- **Social Auth**: Provider-specific loading states

---

## 🔐 Security Implementation

### Authentication Flow
```typescript
// Authentication service
class AuthService {
  async login(email: string, password: string, role: string) {
    // Firebase Auth integration
    const userCredential = await signInWithEmailAndPassword(auth, email, password)
    
    // Role verification
    await this.verifyUserRole(userCredential.user.uid, role)
    
    // Set user context
    return this.setUserSession(userCredential.user, role)
  }

  async register(email: string, password: string, role: string) {
    // Create Firebase user
    const userCredential = await createUserWithEmailAndPassword(auth, email, password)
    
    // Store role in Firestore
    await this.createUserProfile(userCredential.user.uid, { role, email })
    
    return this.setUserSession(userCredential.user, role)
  }
}
```

### Security Features
- **Password Strength**: Real-time strength indicator
- **Rate Limiting**: Prevent brute force attacks
- **Email Verification**: Required for account activation
- **Role Verification**: Server-side role validation
- **Session Management**: Secure token handling

### Privacy Compliance
- **GDPR Compliance**: Clear consent and data usage
- **Data Minimization**: Only collect necessary information
- **Right to Deletion**: Account deletion functionality
- **Privacy Policy**: Clear and accessible privacy terms

---

## 📱 Responsive Behavior

### Breakpoint Adaptations
```css
/* Desktop (1024px+) */
.auth-modal {
  width: 600px;
  max-height: 80vh;
  border-radius: 16px;
}

/* Tablet (768px-1024px) */
.auth-modal {
  width: 90vw;
  max-width: 500px;
}

/* Mobile (320px-768px) */
.auth-modal {
  width: 100vw;
  height: 100vh;
  border-radius: 0;
}
```

### Mobile Optimizations
- **Full-Screen Modal**: Better mobile experience
- **Larger Touch Targets**: 44px minimum for buttons
- **Keyboard Handling**: Proper viewport adjustments
- **Gesture Support**: Swipe to dismiss on mobile

---

## ♿ Accessibility Features

### WCAG 2.1 AA Compliance
- **Focus Management**: Trap focus within modal
- **Keyboard Navigation**: Tab order and escape key
- **Screen Reader**: Proper ARIA labels and announcements
- **Color Contrast**: 4.5:1 ratio for all text
- **Error Handling**: Clear error descriptions

### Implementation Details
```typescript
// Focus management
useEffect(() => {
  if (isOpen) {
    const firstInput = modalRef.current?.querySelector('input')
    firstInput?.focus()
    
    // Trap focus within modal
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }
}, [isOpen])

// ARIA attributes
<div
  role="dialog"
  aria-labelledby="auth-modal-title"
  aria-describedby="auth-modal-description"
  aria-modal="true"
>
```

### Testing Strategy
- [ ] Keyboard-only navigation testing
- [ ] Screen reader compatibility (NVDA, JAWS, VoiceOver)
- [ ] Color blindness simulation
- [ ] High contrast mode support
- [ ] Automated accessibility testing with jest-axe

---

## 📊 Success Metrics

### User Experience Metrics
- **Modal Load Time**: < 200ms
- **Form Completion Rate**: > 85%
- **Authentication Success Rate**: > 95%
- **Error Recovery Rate**: > 90%

### Technical Metrics
- **Bundle Size**: < 50KB for auth components
- **Performance**: 60fps animations
- **Accessibility Score**: 100% automated testing
- **Security**: Zero authentication vulnerabilities

This authentication wireframe provides a modern, secure, and accessible user experience that seamlessly integrates with the CityPulse platform while maintaining the highest standards of usability and security.
