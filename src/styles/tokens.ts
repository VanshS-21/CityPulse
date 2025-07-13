// Basic Design Tokens for CityPulse

export const colors = {
  // Primary Colors
  primary: {
    500: '#3b82f6', // Blue
    600: '#2563eb',
    700: '#1d4ed8',
  },

  // Secondary Colors
  secondary: {
    100: '#f1f5f9',
    500: '#64748b', // Gray
    700: '#334155',
    900: '#0f172a',
  },

  // Status Colors
  success: '#22c55e',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
} as const

// Basic Typography
export const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
    mono: ['monospace'],
  },
} as const

// Basic Spacing
export const spacing = {
  1: '0.25rem',
  2: '0.5rem',
  4: '1rem',
  8: '2rem',
  16: '4rem',
} as const


