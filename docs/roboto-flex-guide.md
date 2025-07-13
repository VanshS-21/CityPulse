# Roboto Flex Implementation Guide for CityPulse

## Overview

CityPulse now uses **Roboto Flex**as its primary typeface. Roboto Flex is a variable font that
provides exceptional flexibility with adjustable weight and optical sizing, making it perfect for
our urban intelligence platform.

## What's Implemented

### 1. Font Loading

- **Google Fonts Integration**: Roboto Flex is loaded via Google Fonts in `src/app/layout.tsx`-
  **Variable Font Settings**: Full weight range (100-1000) and optical sizing (8-144) enabled

- **Performance Optimized**: Uses`font-display: swap`for better loading performance

### 2. CSS Configuration

- **Primary Font**: Roboto Flex is now the primary font in`globals.css`- **Fallback Chain**: Robust
  fallback to Inter, system fonts, and sans-serif

- **CSS Variables**: Updated to prioritize Roboto Flex in the font stack

### 3. Tailwind Configuration

- **Font Families**: Updated Tailwind config to use Roboto Flex as primary
- **Additional Font Stack**: Added`font-flex`utility for explicit Roboto Flex usage

## Variable Font Features

### Weight Variations

Roboto Flex supports variable weights from 100 to 1000:```css /_CSS Custom Properties_/ .font-thin {
font-variation-settings: 'wght' 100; } .font-extralight { font-variation-settings: 'wght' 200; }
.font-light { font-variation-settings: 'wght' 300; } .font-normal { font-variation-settings: 'wght'
400; } .font-medium { font-variation-settings: 'wght' 500; } .font-semibold {
font-variation-settings: 'wght' 600; } .font-bold { font-variation-settings: 'wght' 700; }
.font-extrabold { font-variation-settings: 'wght' 800; } .font-black { font-variation-settings:
'wght' 900; }

````text

### Optical Sizing

Optical sizing automatically adjusts the font for different text sizes:

```css

/*Optical Size Variations*/
.text-optical-sm { font-variation-settings: 'opsz' 8; }    /*Small text*/
.text-optical-base { font-variation-settings: 'opsz' 14; } /*Body text*/
.text-optical-lg { font-variation-settings: 'opsz' 18; }   /*Large text*/
.text-optical-xl { font-variation-settings: 'opsz' 24; }   /*Extra large*/
.text-optical-2xl { font-variation-settings: 'opsz' 32; }  /*Headings*/
.text-optical-3xl { font-variation-settings: 'opsz' 48; }  /*Large headings*/
.text-optical-4xl { font-variation-settings: 'opsz' 64; }  /*Display text*/
.text-optical-5xl { font-variation-settings: 'opsz' 96; }  /*Hero text*/
.text-optical-6xl { font-variation-settings: 'opsz' 144; } /*Maximum size*/

```text

## CityPulse Typography Presets

We've created semantic typography classes that combine weight and optical sizing:

### Usage Examples

```jsx

// Headings
<h1 className="font-heading text-4xl">CityPulse Dashboard</h1>
<h2 className="font-subheading text-2xl">Traffic Analytics</h2>

// Body text
<p className="font-body">Regular content with optimal readability</p>

// UI Elements
<button className="font-button px-4 py-2">Action Button</button>
<span className="font-caption text-sm">Helper text</span>

// Display text
<div className="font-display text-6xl">98.5%</div>
<h1 className="font-hero text-8xl">CityPulse</h1>

```text

### Preset Classes

| Class | Weight | Optical Size | Use Case |
|-------|--------|-------------|----------|
| `.font-heading`| 600 | 32 | Section headings |
|`.font-subheading`| 500 | 18 | Subsection headings |
|`.font-body`| 400 | 14 | Body text, paragraphs |
|`.font-caption`| 400 | 8 | Small text, captions |
|`.font-button`| 500 | 14 | Button labels |
|`.font-display`| 700 | 64 | Large metrics, statistics |
|`.font-hero`| 800 | 96 | Hero titles, main headers |

## Best Practices

### 1. Use Semantic Classes

Prefer semantic typography classes over generic weight classes:```jsx
// ✅ Good - Semantic and consistent
<h2 className="font-heading">System Status</h2>

// ❌ Avoid - Generic and inconsistent
<h2 className="font-semibold">System Status</h2>
```text

### 2. Combine with Tailwind Text Sizes

The preset classes work with Tailwind's text sizing:

```jsx
<h1 className="font-hero text-6xl md:text-8xl">CityPulse</h1>
<h2 className="font-heading text-2xl md:text-4xl">Analytics</h2>
<p className="font-body text-base">Content description</p>
```text

### 3. Letter Spacing

Some presets include optimized letter spacing:

-   **Headings**: Negative letter spacing for tighter appearance
-   **Display text**: More negative spacing for large sizes
-   **Captions**: Slight positive spacing for readability

### 4. Responsive Typography

Use responsive modifiers for different screen sizes:

```jsx
<h1 className="font-hero text-4xl md:text-6xl lg:text-8xl">
  Smart City Dashboard
</h1>
```text

## Performance Considerations

### 1. Font Loading 2

-   Roboto Flex loads asynchronously with `font-display: swap`-  Fallback fonts ensure immediate text rendering
-   Consider using`font-optical-sizing: auto`in CSS for automatic optimization

### 2. Variable Font Efficiency

-   Single font file supports all weights and optical sizes
-   Reduces HTTP requests compared to multiple font files
-   Smaller total file size than loading multiple weights

### 3. Browser Support

-   Excellent support in modern browsers
-   Graceful fallback to system fonts in older browsers
-   Progressive enhancement approach

## Migration Guide

### From Existing Components

1.  Remove explicit font weight classes where semantic classes exist
1.  Add optical sizing for better text rendering
1.  Use preset classes for consistency```jsx
// Before
<h1 className="text-4xl font-bold">Dashboard</h1>
<p className="text-base font-normal">Content</p>

// After
<h1 className="text-4xl font-heading">Dashboard</h1>
<p className="text-base font-body">Content</p>

```text

### Custom Combinations

For unique cases, combine optical sizing with weight:

```jsx

<span className="text-optical-lg font-medium">
  Custom styled text
</span>

```text

## Troubleshooting

### Font Not Loading

1.  Check network requests for Google Fonts
1.  Verify `layout.tsx`has correct font links
1.  Ensure fallback fonts are working

### Inconsistent Rendering

1.  Use semantic classes instead of generic weights
1.  Check for conflicting CSS
1.  Verify optical sizing is appropriate for text size

### Performance Issues

1.  Ensure`font-display: swap` is set
1.  Consider preloading critical font variations
1.  Check for unused font weights

## Future Enhancements

-   **Custom Optical Sizing**: Fine-tune optical sizing for specific CityPulse use cases
-   **Font Loading Optimization**: Implement more advanced loading strategies
-   **Theme Integration**: Better integration with dark/light theme variations
-   **Animation Support**: Smooth transitions between font variations

## Resources

-   [Roboto Flex on Google Fonts](https://fonts.google.com/specimen/Roboto+Flex)
-   [Variable Fonts Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Fonts/Variable_Fonts_Guide)
-   [CSS font-variation-settings](https://developer.mozilla.org/en-US/docs/Web/CSS/font-variation-settings)
````
