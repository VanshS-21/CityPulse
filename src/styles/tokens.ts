/**
 * CityPulse Design System - Design Tokens
 * Comprehensive design tokens extracted from wireframes and modern design patterns
 */

// ============================================================================
// COLOR SYSTEM - Inspired by Urban Environments and Civic Trust
// ============================================================================

export const colorTokens = {
  // Brand Colors - Primary Blues for Trust & Reliability
  brand: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',  // Main brand color from wireframes
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
      950: '#172554',
    },
    secondary: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',  // Urban gray from wireframes
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a',
      950: '#020617',
    },
  },

  // Semantic Colors - Clear System Feedback
  semantic: {
    success: {
      50: '#f0fdf4',
      100: '#dcfce7',
      200: '#bbf7d0',
      300: '#86efac',
      400: '#4ade80',
      500: '#22c55e',  // Issue resolved
      600: '#16a34a',
      700: '#15803d',
      800: '#166534',
      900: '#14532d',
    },
    warning: {
      50: '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',  // Issue pending
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f',
    },
    error: {
      50: '#fef2f2',
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',  // Issue urgent
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d',
    },
    info: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',  // Information
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
  },

  // Neutral Colors - Professional Urban Architecture
  neutral: {
    0: '#ffffff',
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
    950: '#030712',
  },

  // Glassmorphism Colors - Modern Translucent Effects
  glass: {
    white: {
      5: 'rgba(255, 255, 255, 0.05)',
      10: 'rgba(255, 255, 255, 0.1)',
      15: 'rgba(255, 255, 255, 0.15)',
      20: 'rgba(255, 255, 255, 0.2)',
      25: 'rgba(255, 255, 255, 0.25)',
    },
    black: {
      5: 'rgba(0, 0, 0, 0.05)',
      10: 'rgba(0, 0, 0, 0.1)',
      15: 'rgba(0, 0, 0, 0.15)',
      20: 'rgba(0, 0, 0, 0.2)',
      25: 'rgba(0, 0, 0, 0.25)',
    },
  },
} as const;

// Semantic Color Mappings from Wireframe Context
export const semanticColors = {
  // Background Colors
  bg: {
    primary: colorTokens.neutral[0],
    secondary: colorTokens.neutral[50],
    tertiary: colorTokens.neutral[100],
    inverse: colorTokens.neutral[900],
    glass: colorTokens.glass.white[10],
    glassElevated: colorTokens.glass.white[15],
  },

  // Text Colors
  text: {
    primary: colorTokens.neutral[900],
    secondary: colorTokens.neutral[600],
    tertiary: colorTokens.neutral[500],
    inverse: colorTokens.neutral[0],
    brand: colorTokens.brand.primary[600],
    muted: colorTokens.neutral[400],
  },

  // Border Colors
  border: {
    primary: colorTokens.neutral[200],
    secondary: colorTokens.neutral[300],
    focus: colorTokens.brand.primary[500],
    glass: colorTokens.glass.white[20],
  },

  // Status Colors for UI Elements
  status: {
    success: colorTokens.semantic.success[500],
    warning: colorTokens.semantic.warning[500],
    error: colorTokens.semantic.error[500],
    info: colorTokens.semantic.info[500],
  },
} as const;

// ============================================================================
// TYPOGRAPHY SYSTEM - Optimized for Data Consumption
// ============================================================================

export const typographyTokens = {
  // Font Families
  fontFamily: {
    sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
    serif: ['Georgia', 'Cambria', 'Times New Roman', 'serif'],
    mono: ['Fira Code', 'Monaco', 'Consolas', 'Liberation Mono', 'monospace'],
    display: ['Inter', 'system-ui', 'sans-serif'], // For headings and hero text
  },

  // Font Sizes - Extracted from Wireframes
  fontSize: {
    '2xs': ['0.625rem', { lineHeight: '1rem' }],     // 10px
    'xs': ['0.75rem', { lineHeight: '1.125rem' }],   // 12px
    'sm': ['0.875rem', { lineHeight: '1.25rem' }],   // 14px
    'base': ['1rem', { lineHeight: '1.5rem' }],      // 16px - base size
    'lg': ['1.125rem', { lineHeight: '1.75rem' }],   // 18px
    'xl': ['1.25rem', { lineHeight: '1.75rem' }],    // 20px
    '2xl': ['1.5rem', { lineHeight: '2rem' }],       // 24px
    '3xl': ['1.875rem', { lineHeight: '2.25rem' }],  // 30px
    '4xl': ['2.25rem', { lineHeight: '2.5rem' }],    // 36px - hero text
    '5xl': ['3rem', { lineHeight: '1' }],            // 48px
    '6xl': ['3.75rem', { lineHeight: '1' }],         // 60px
    '7xl': ['4.5rem', { lineHeight: '1' }],          // 72px
    '8xl': ['6rem', { lineHeight: '1' }],            // 96px
    '9xl': ['8rem', { lineHeight: '1' }],            // 128px
  },

  // Font Weights
  fontWeight: {
    thin: '100',
    extralight: '200',
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
    black: '900',
  },

  // Line Heights
  lineHeight: {
    none: '1',
    tight: '1.25',
    snug: '1.375',
    normal: '1.5',
    relaxed: '1.625',
    loose: '2',
  },

  // Letter Spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0em',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
} as const;

// Typography Presets from Wireframe Patterns
export const typographyPresets = {
  // Display Text - Hero Sections
  display: {
    '2xl': {
      fontSize: typographyTokens.fontSize['6xl'],
      fontWeight: typographyTokens.fontWeight.bold,
      lineHeight: typographyTokens.lineHeight.none,
      letterSpacing: typographyTokens.letterSpacing.tight,
      fontFamily: typographyTokens.fontFamily.display,
    },
    'xl': {
      fontSize: typographyTokens.fontSize['5xl'],
      fontWeight: typographyTokens.fontWeight.bold,
      lineHeight: typographyTokens.lineHeight.tight,
      letterSpacing: typographyTokens.letterSpacing.tight,
    },
    'lg': {
      fontSize: typographyTokens.fontSize['4xl'],
      fontWeight: typographyTokens.fontWeight.bold,
      lineHeight: typographyTokens.lineHeight.tight,
    },
  },

  // Headings - Section Headers
  heading: {
    'h1': {
      fontSize: typographyTokens.fontSize['3xl'],
      fontWeight: typographyTokens.fontWeight.bold,
      lineHeight: typographyTokens.lineHeight.tight,
    },
    'h2': {
      fontSize: typographyTokens.fontSize['2xl'],
      fontWeight: typographyTokens.fontWeight.semibold,
      lineHeight: typographyTokens.lineHeight.tight,
    },
    'h3': {
      fontSize: typographyTokens.fontSize['xl'],
      fontWeight: typographyTokens.fontWeight.semibold,
      lineHeight: typographyTokens.lineHeight.snug,
    },
    'h4': {
      fontSize: typographyTokens.fontSize['lg'],
      fontWeight: typographyTokens.fontWeight.semibold,
      lineHeight: typographyTokens.lineHeight.snug,
    },
  },

  // Body Text - Content
  body: {
    'lg': {
      fontSize: typographyTokens.fontSize['lg'],
      fontWeight: typographyTokens.fontWeight.normal,
      lineHeight: typographyTokens.lineHeight.relaxed,
    },
    'base': {
      fontSize: typographyTokens.fontSize['base'],
      fontWeight: typographyTokens.fontWeight.normal,
      lineHeight: typographyTokens.lineHeight.normal,
    },
    'sm': {
      fontSize: typographyTokens.fontSize['sm'],
      fontWeight: typographyTokens.fontWeight.normal,
      lineHeight: typographyTokens.lineHeight.normal,
    },
  },

  // Labels and Captions
  label: {
    'lg': {
      fontSize: typographyTokens.fontSize['base'],
      fontWeight: typographyTokens.fontWeight.medium,
      lineHeight: typographyTokens.lineHeight.normal,
    },
    'base': {
      fontSize: typographyTokens.fontSize['sm'],
      fontWeight: typographyTokens.fontWeight.medium,
      lineHeight: typographyTokens.lineHeight.normal,
    },
    'sm': {
      fontSize: typographyTokens.fontSize['xs'],
      fontWeight: typographyTokens.fontWeight.medium,
      lineHeight: typographyTokens.lineHeight.normal,
    },
  },

  // Caption and Helper Text
  caption: {
    fontSize: typographyTokens.fontSize['sm'],
    fontWeight: typographyTokens.fontWeight.normal,
    lineHeight: typographyTokens.lineHeight.snug,
    color: semanticColors.text.secondary,
  },
} as const;

// ============================================================================
// SPACING SYSTEM - 8px Grid System from Wireframes
// ============================================================================

export const spacingTokens = {
  // Base spacing unit (8px grid)
  0: '0',
  px: '1px',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px - base unit
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  3.5: '0.875rem',  // 14px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  7: '1.75rem',     // 28px
  8: '2rem',        // 32px
  9: '2.25rem',     // 36px
  10: '2.5rem',     // 40px
  11: '2.75rem',    // 44px - minimum touch target
  12: '3rem',       // 48px
  14: '3.5rem',     // 56px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
  28: '7rem',       // 112px
  32: '8rem',       // 128px
  36: '9rem',       // 144px
  40: '10rem',      // 160px
  44: '11rem',      // 176px
  48: '12rem',      // 192px
  52: '13rem',      // 208px
  56: '14rem',      // 224px
  60: '15rem',      // 240px
  64: '16rem',      // 256px
  72: '18rem',      // 288px
  80: '20rem',      // 320px
  96: '24rem',      // 384px
} as const;

// Semantic Spacing from Wireframe Patterns
export const semanticSpacing = {
  // Component Internal Spacing
  component: {
    xs: spacingTokens[1],    // 4px - tight spacing
    sm: spacingTokens[2],    // 8px - small spacing
    md: spacingTokens[4],    // 16px - medium spacing
    lg: spacingTokens[6],    // 24px - large spacing
    xl: spacingTokens[8],    // 32px - extra large spacing
    '2xl': spacingTokens[12], // 48px - huge spacing
  },

  // Layout Spacing
  layout: {
    xs: spacingTokens[4],    // 16px
    sm: spacingTokens[6],    // 24px
    md: spacingTokens[8],    // 32px
    lg: spacingTokens[12],   // 48px
    xl: spacingTokens[16],   // 64px
    '2xl': spacingTokens[24], // 96px
  },

  // Section Spacing
  section: {
    xs: spacingTokens[8],    // 32px
    sm: spacingTokens[12],   // 48px
    md: spacingTokens[16],   // 64px
    lg: spacingTokens[24],   // 96px
    xl: spacingTokens[32],   // 128px
    '2xl': spacingTokens[48], // 192px
  },
} as const;

// ============================================================================
// ELEVATION SYSTEM - Shadows and Depth
// ============================================================================

export const elevationTokens = {
  // Box Shadows for Depth
  shadow: {
    none: 'none',
    xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
  },

  // Glassmorphism Shadows
  glassShadow: {
    sm: '0 4px 16px rgba(0, 0, 0, 0.1)',
    md: '0 8px 32px rgba(0, 0, 0, 0.1)',
    lg: '0 16px 48px rgba(0, 0, 0, 0.15)',
    xl: '0 24px 64px rgba(0, 0, 0, 0.2)',
  },

  // Z-Index Scale
  zIndex: {
    hide: -1,
    auto: 'auto',
    base: 0,
    docked: 10,
    dropdown: 1000,
    sticky: 1100,
    banner: 1200,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    skipLink: 1600,
    toast: 1700,
    tooltip: 1800,
  },
} as const;

// ============================================================================
// MOTION SYSTEM - Animation and Transitions
// ============================================================================

export const motionTokens = {
  // Duration Scale
  duration: {
    instant: '0ms',
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
    slower: '750ms',
    slowest: '1000ms',
  },

  // Easing Functions
  easing: {
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    elastic: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
  },

  // Common Transition Presets
  transition: {
    fast: 'all 150ms cubic-bezier(0, 0, 0.2, 1)',
    normal: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: 'all 500ms cubic-bezier(0.4, 0, 0.2, 1)',
    colors: 'color 150ms cubic-bezier(0, 0, 0.2, 1), background-color 150ms cubic-bezier(0, 0, 0.2, 1), border-color 150ms cubic-bezier(0, 0, 0.2, 1)',
    transform: 'transform 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    opacity: 'opacity 300ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
} as const;

// ============================================================================
// BREAKPOINT SYSTEM - Responsive Design
// ============================================================================

export const breakpointTokens = {
  // Breakpoint Values
  values: {
    xs: '320px',   // Mobile small
    sm: '640px',   // Mobile large
    md: '768px',   // Tablet
    lg: '1024px',  // Desktop small
    xl: '1280px',  // Desktop large
    '2xl': '1536px', // Desktop extra large
  },

  // Media Queries
  media: {
    xs: '@media (min-width: 320px)',
    sm: '@media (min-width: 640px)',
    md: '@media (min-width: 768px)',
    lg: '@media (min-width: 1024px)',
    xl: '@media (min-width: 1280px)',
    '2xl': '@media (min-width: 1536px)',
  },

  // Container Max Widths
  container: {
    xs: '100%',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
} as const;

// ============================================================================
// BORDER RADIUS SYSTEM
// ============================================================================

export const borderRadiusTokens = {
  none: '0',
  xs: '0.125rem',   // 2px
  sm: '0.25rem',    // 4px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px - glassmorphism cards
  '3xl': '1.5rem',  // 24px
  full: '9999px',   // Pills and circles
} as const;

// Export all tokens as a unified design system
export const designTokens = {
  colors: colorTokens,
  semanticColors,
  typography: typographyTokens,
  typographyPresets,
  spacing: spacingTokens,
  semanticSpacing,
  elevation: elevationTokens,
  motion: motionTokens,
  breakpoints: breakpointTokens,
  borderRadius: borderRadiusTokens,
} as const;

// Type definitions for TypeScript
export type ColorTokens = typeof colorTokens;
export type TypographyTokens = typeof typographyTokens;
export type SpacingTokens = typeof spacingTokens;
export type ElevationTokens = typeof elevationTokens;
export type MotionTokens = typeof motionTokens;
export type BreakpointTokens = typeof breakpointTokens;
export type DesignTokens = typeof designTokens;


