/** @type {import('tailwindcss').Config} */
const { designTokens } = require('./src/styles/tokens');

module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    // Override default Tailwind theme with our design tokens
    colors: {
      // Brand colors from design tokens
      primary: designTokens.colors.brand.primary,
      secondary: designTokens.colors.brand.secondary,

      // Semantic colors
      success: designTokens.colors.semantic.success,
      warning: designTokens.colors.semantic.warning,
      error: designTokens.colors.semantic.error,
      info: designTokens.colors.semantic.info,

      // Neutral colors
      neutral: designTokens.colors.neutral,

      // Glassmorphism colors
      glass: designTokens.colors.glass,

      // Transparent and current
      transparent: 'transparent',
      current: 'currentColor',

      // Legacy shadcn/ui compatibility
      background: 'var(--background)',
      foreground: 'var(--foreground)',
      card: {
        DEFAULT: 'var(--card)',
        foreground: 'var(--card-foreground)',
      },
      muted: {
        DEFAULT: 'var(--muted)',
        foreground: 'var(--muted-foreground)',
      },
      border: 'var(--border)',
      input: 'var(--input)',
      ring: 'var(--ring)',
    },

    // Typography from design tokens
    fontFamily: designTokens.typography.fontFamily,
    fontSize: designTokens.typography.fontSize,
    fontWeight: designTokens.typography.fontWeight,
    lineHeight: designTokens.typography.lineHeight,
    letterSpacing: designTokens.typography.letterSpacing,

    // Spacing from design tokens
    spacing: designTokens.spacing,

    // Border radius from design tokens
    borderRadius: {
      ...designTokens.borderRadius,
      // Legacy shadcn/ui compatibility
      lg: 'var(--radius)',
      md: 'calc(var(--radius) - 2px)',
      sm: 'calc(var(--radius) - 4px)',
    },

    // Box shadows from design tokens
    boxShadow: designTokens.elevation.shadow,

    // Z-index from design tokens
    zIndex: designTokens.elevation.zIndex,

    // Breakpoints from design tokens
    screens: {
      xs: designTokens.breakpoints.values.xs,
      sm: designTokens.breakpoints.values.sm,
      md: designTokens.breakpoints.values.md,
      lg: designTokens.breakpoints.values.lg,
      xl: designTokens.breakpoints.values.xl,
      '2xl': designTokens.breakpoints.values['2xl'],
    },

    // Animation timing from design tokens
    transitionDuration: designTokens.motion.duration,
    transitionTimingFunction: designTokens.motion.easing,

    extend: {
      // Glassmorphism utilities
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
        'md': '12px',
        'lg': '20px',
        'xl': '30px',
        '2xl': '40px',
        '3xl': '64px',
      },

      // Glass shadows for glassmorphism
      boxShadow: {
        'glass-sm': designTokens.elevation.glassShadow.sm,
        'glass-md': designTokens.elevation.glassShadow.md,
        'glass-lg': designTokens.elevation.glassShadow.lg,
        'glass-xl': designTokens.elevation.glassShadow.xl,
      },

      // Animation utilities
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-gentle': 'bounceGentle 2s infinite',
      },

      // Keyframes for animations
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },

      // Container utilities
      container: {
        center: true,
        padding: {
          DEFAULT: designTokens.spacing[4],
          sm: designTokens.spacing[6],
          lg: designTokens.spacing[8],
          xl: designTokens.spacing[12],
          '2xl': designTokens.spacing[16],
        },
        screens: designTokens.breakpoints.container,
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
    // Custom glassmorphism utilities
    function({ addUtilities }) {
      const glassUtilities = {
        '.glass': {
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        },
        '.glass-elevated': {
          background: 'rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(30px)',
          border: '1px solid rgba(255, 255, 255, 0.25)',
        },
        '.glass-dark': {
          background: 'rgba(0, 0, 0, 0.1)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
      };
      addUtilities(glassUtilities);
    },
  ],
}
