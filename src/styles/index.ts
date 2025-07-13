/**
 * CityPulse Design System - Main Export
 * Centralized export for all design system tokens, utilities, and types
 */

// Export all design tokens
export {
  colorTokens,
  semanticColors,
  typographyTokens,
  typographyPresets,
  spacingTokens,
  semanticSpacing,
  elevationTokens,
  motionTokens,
  breakpointTokens,
  borderRadiusTokens,
  designTokens,
} from './tokens';

// Export TypeScript types
export type {
  ColorTokens,
  TypographyTokens,
  SpacingTokens,
  ElevationTokens,
  MotionTokens,
  BreakpointTokens,
  DesignTokens,
} from './tokens';

// Design System Configuration
export const designSystemConfig = {
  version: '1.0.0',
  name: 'CityPulse Design System',
  description: 'Modern urban intelligence platform design language',
  
  // Feature flags for design system capabilities
  features: {
    glassmorphism: true,
    animations: true,
    darkMode: true,
    accessibility: true,
    responsiveDesign: true,
    customProperties: true,
  },
  
  // Browser support
  browserSupport: {
    chrome: '90+',
    firefox: '88+',
    safari: '14+',
    edge: '90+',
  },
  
  // Performance targets
  performance: {
    bundleSize: '< 50KB',
    animationFPS: 60,
    loadTime: '< 3s',
    accessibility: 'WCAG 2.1 AA',
  },
} as const;

// Utility functions for design system
export const designSystemUtils = {
  // Get color value by path
  getColor: (path: string) => {
    const keys = path.split('.');
    let value: any = designTokens.colors;
    
    for (const key of keys) {
      value = value?.[key];
    }
    
    return value || null;
  },
  
  // Get spacing value
  getSpacing: (key: keyof typeof designTokens.spacing) => {
    return designTokens.spacing[key];
  },
  
  // Get typography preset
  getTypography: (preset: string) => {
    const presets = designTokens.typographyPresets as any;
    return presets[preset] || null;
  },
  
  // Get elevation (shadow) value
  getElevation: (level: keyof typeof designTokens.elevation.shadow) => {
    return designTokens.elevation.shadow[level];
  },
  
  // Get motion timing
  getMotion: (type: keyof typeof designTokens.motion.duration) => {
    return designTokens.motion.duration[type];
  },
  
  // Get breakpoint value
  getBreakpoint: (size: keyof typeof designTokens.breakpoints.values) => {
    return designTokens.breakpoints.values[size];
  },
  
  // Generate CSS custom properties
  generateCSSCustomProperties: () => {
    const cssVars: Record<string, string> = {};
    
    // Generate color variables
    Object.entries(designTokens.colors.brand.primary).forEach(([key, value]) => {
      cssVars[`--color-primary-${key}`] = value;
    });
    
    Object.entries(designTokens.colors.brand.secondary).forEach(([key, value]) => {
      cssVars[`--color-secondary-${key}`] = value;
    });
    
    // Generate spacing variables
    Object.entries(designTokens.spacing).forEach(([key, value]) => {
      cssVars[`--spacing-${key}`] = value;
    });
    
    // Generate typography variables
    Object.entries(designTokens.typography.fontSize).forEach(([key, value]) => {
      cssVars[`--font-size-${key}`] = Array.isArray(value) ? value[0] : value;
    });
    
    return cssVars;
  },
  
  // Validate design token usage
  validateToken: (category: string, token: string) => {
    const categories = {
      color: designTokens.colors,
      spacing: designTokens.spacing,
      typography: designTokens.typography,
      elevation: designTokens.elevation,
      motion: designTokens.motion,
      breakpoints: designTokens.breakpoints,
    } as any;
    
    return categories[category]?.[token] !== undefined;
  },
  
  // Get responsive value
  getResponsiveValue: (values: Record<string, any>) => {
    const breakpoints = designTokens.breakpoints.values;
    const sortedBreakpoints = Object.entries(breakpoints).sort(
      ([, a], [, b]) => parseInt(a) - parseInt(b)
    );
    
    return sortedBreakpoints.reduce((acc, [key]) => {
      if (values[key]) {
        acc[`@media (min-width: ${breakpoints[key as keyof typeof breakpoints]})`] = values[key];
      }
      return acc;
    }, {} as Record<string, any>);
  },
} as const;

// Component prop types for design system
export interface DesignSystemProps {
  // Color props
  color?: keyof typeof designTokens.colors.brand.primary;
  bg?: keyof typeof designTokens.colors.brand.primary;
  
  // Spacing props
  p?: keyof typeof designTokens.spacing;
  px?: keyof typeof designTokens.spacing;
  py?: keyof typeof designTokens.spacing;
  pt?: keyof typeof designTokens.spacing;
  pr?: keyof typeof designTokens.spacing;
  pb?: keyof typeof designTokens.spacing;
  pl?: keyof typeof designTokens.spacing;
  m?: keyof typeof designTokens.spacing;
  mx?: keyof typeof designTokens.spacing;
  my?: keyof typeof designTokens.spacing;
  mt?: keyof typeof designTokens.spacing;
  mr?: keyof typeof designTokens.spacing;
  mb?: keyof typeof designTokens.spacing;
  ml?: keyof typeof designTokens.spacing;
  
  // Typography props
  fontSize?: keyof typeof designTokens.typography.fontSize;
  fontWeight?: keyof typeof designTokens.typography.fontWeight;
  lineHeight?: keyof typeof designTokens.typography.lineHeight;
  letterSpacing?: keyof typeof designTokens.typography.letterSpacing;
  
  // Layout props
  w?: string | number;
  h?: string | number;
  maxW?: string | number;
  maxH?: string | number;
  minW?: string | number;
  minH?: string | number;
  
  // Flexbox props
  display?: 'flex' | 'inline-flex' | 'block' | 'inline-block' | 'none';
  flexDirection?: 'row' | 'column' | 'row-reverse' | 'column-reverse';
  justifyContent?: 'flex-start' | 'flex-end' | 'center' | 'space-between' | 'space-around' | 'space-evenly';
  alignItems?: 'flex-start' | 'flex-end' | 'center' | 'baseline' | 'stretch';
  flexWrap?: 'nowrap' | 'wrap' | 'wrap-reverse';
  gap?: keyof typeof designTokens.spacing;
  
  // Border props
  borderRadius?: keyof typeof designTokens.borderRadius;
  border?: boolean;
  borderColor?: string;
  borderWidth?: string | number;
  
  // Shadow props
  shadow?: keyof typeof designTokens.elevation.shadow;
  
  // Animation props
  transition?: keyof typeof designTokens.motion.transition;
  duration?: keyof typeof designTokens.motion.duration;
  easing?: keyof typeof designTokens.motion.easing;
}

// Theme context type
export interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  tokens: typeof designTokens;
  utils: typeof designSystemUtils;
}

// Responsive breakpoint hooks
export const useBreakpoint = () => {
  const breakpoints = designTokens.breakpoints.values;
  
  return {
    xs: `(min-width: ${breakpoints.xs})`,
    sm: `(min-width: ${breakpoints.sm})`,
    md: `(min-width: ${breakpoints.md})`,
    lg: `(min-width: ${breakpoints.lg})`,
    xl: `(min-width: ${breakpoints.xl})`,
    '2xl': `(min-width: ${breakpoints['2xl']})`,
  };
};

// Animation presets
export const animationPresets = {
  // Entrance animations
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  
  slideDown: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  
  scaleIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    transition: { duration: 0.2, ease: 'easeOut' },
  },
  
  // Stagger animations
  stagger: {
    animate: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  },
  
  // Hover animations
  hover: {
    whileHover: {
      y: -2,
      transition: { duration: 0.2, ease: 'easeOut' },
    },
  },
  
  // Tap animations
  tap: {
    whileTap: {
      scale: 0.98,
      transition: { duration: 0.1, ease: 'easeOut' },
    },
  },
} as const;

// Export everything as default
export default {
  tokens: designTokens,
  utils: designSystemUtils,
  config: designSystemConfig,
  animationPresets,
  useBreakpoint,
};
