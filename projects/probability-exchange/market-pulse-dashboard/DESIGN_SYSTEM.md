# Market Pulse Design System - Quick Reference

## Color Tokens

### Primary Palette
```css
--primary-50:  #f0f4ff
--primary-100: #e0e9ff
--primary-200: #c7d7ff
--primary-300: #a5bfff
--primary-400: #8099ff
--primary-500: #6366f1  /* Main brand */
--primary-600: #4f46e5
--primary-700: #4338ca
--primary-800: #3730a3
--primary-900: #312e81
```

### Semantic Colors
```css
--success-500: #10b981
--danger-500:  #ef4444
--warning-500: #f59e0b
```

### Dark Theme
```css
--dark-bg:      #050505  /* Base background */
--dark-surface: #0a0a0a  /* Elevated surface */
--dark-card:    #0f0f0f  /* Card background */
--dark-border:  rgba(255, 255, 255, 0.08)
--dark-hover:   rgba(255, 255, 255, 0.05)
```

### Zinc Scale (Gray Tones)
```css
--zinc-100: #f4f4f5  /* Light text */
--zinc-300: #d4d4d8
--zinc-400: #a1a1aa
--zinc-500: #71717a  /* Secondary text */
--zinc-600: #52525b
--zinc-700: #3f3f46
--zinc-800: #27272a  /* Muted elements */
```

## Typography

### Font Families
```css
--font-sans: 'Inter', system-ui, sans-serif;
--font-mono: 'IBM Plex Mono', 'Menlo', monospace;
```

### Font Sizes
```css
--text-xs:   0.75rem  /* 12px - Labels */
--text-sm:   0.875rem /* 14px - Secondary */
--text-base: 1rem     /* 16px - Body */
--text-lg:   1.125rem /* 18px - Subheading */
--text-xl:   1.25rem  /* 20px - Heading */
--text-2xl:  1.5rem   /* 24px - Stats */
--text-3xl:  1.875rem /* 30px - Section */
--text-5xl:  3rem     /* 48px - Hero price */
```

### Font Weights
```css
--font-normal:    400
--font-medium:    500
--font-semibold:  600
--font-bold:      700
--font-extrabold: 800
```

## Spacing Scale

```css
--spacing-1:  0.25rem  /* 4px */
--spacing-2:  0.5rem   /* 8px */
--spacing-3:  0.75rem  /* 12px */
--spacing-4:  1rem     /* 16px */
--spacing-6:  1.5rem   /* 24px */
--spacing-8:  2rem     /* 32px */
--spacing-12: 3rem     /* 48px */
--spacing-16: 4rem     /* 64px */
```

## Border Radius

```css
--radius-lg:   0.5rem   /* 8px - Buttons, badges */
--radius-xl:   0.75rem  /* 12px - Inputs */
--radius-2xl:  1rem     /* 16px - Cards */
--radius-full: 9999px   /* Pills, circles */
```

## Shadows & Glows

```css
--shadow-glow-sm: 0 0 10px rgba(99, 102, 241, 0.3);
--shadow-glow-md: 0 0 20px rgba(99, 102, 241, 0.4);
--shadow-glow-lg: 0 0 30px rgba(99, 102, 241, 0.5);
```

## Animations

### Durations
```css
--duration-fast:   150ms
--duration-base:   200ms
--duration-medium: 300ms
--duration-slow:   500ms
```

### Easing
```css
--ease-out: cubic-bezier(0.4, 0, 0.2, 1)
--ease-in:  cubic-bezier(0.4, 0, 1, 1)
```

### Keyframes
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.5; }
}

@keyframes slideUp {
  from { transform: translateY(10px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to   { transform: scale(1); opacity: 1; }
}

@keyframes priceFlash {
  from { background-color: rgba(99, 102, 241, 0.3); }
  to   { background-color: transparent; }
}
```

## Component Patterns

### Card
```tsx
<div className="bg-dark-card/60 backdrop-blur-sm rounded-2xl border border-dark-border p-6">
  {/* Content */}
</div>
```

### Button - Primary
```tsx
<button className="px-5 py-2 rounded-xl bg-gradient-primary text-white font-semibold hover:scale-105 transition-transform">
  Action
</button>
```

### Button - Secondary
```tsx
<button className="px-5 py-2 rounded-xl bg-dark-surface border border-dark-border hover:border-primary-500/50 transition-colors">
  Action
</button>
```

### Input
```tsx
<input className="w-full px-4 py-3 rounded-2xl bg-dark-surface/80 border border-dark-border text-white placeholder-zinc-600 focus:outline-none focus:border-primary-500/50 transition-all" />
```

### Badge
```tsx
<span className="px-3 py-1 rounded-lg bg-primary-500/20 text-primary-400 border border-primary-500/30 text-xs font-semibold">
  Badge
</span>
```

### Status Indicator
```tsx
<span className="relative flex h-2 w-2">
  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-500 opacity-75" />
  <span className="relative inline-flex rounded-full h-2 w-2 bg-success-500" />
</span>
```

## Usage Guidelines

### When to Use Gradients
✅ Logo/branding elements
✅ Hover states (subtle)
✅ Background ambience
❌ Text (hard to read)
❌ Every element (overwhelming)

### When to Use Animations
✅ State changes (loading → loaded)
✅ User feedback (hover, click)
✅ Data updates (price changes)
❌ Decorative motion
❌ Complex sequences

### Accessibility Checklist
- [ ] 4.5:1 contrast for body text
- [ ] 3:1 contrast for large text
- [ ] Focus visible on all interactive elements
- [ ] Keyboard navigation works
- [ ] ARIA labels on icon-only buttons
- [ ] Motion can be disabled

## Platform-Specific Colors

### Kalshi
```css
--kalshi-bg:     rgba(59, 130, 246, 0.2)
--kalshi-text:   #60a5fa
--kalshi-border: rgba(59, 130, 246, 0.3)
```

### Polymarket
```css
--polymarket-bg:     rgba(168, 85, 247, 0.2)
--polymarket-text:   #c084fc
--polymarket-border: rgba(168, 85, 247, 0.3)
```

### Manifold
```css
--manifold-bg:     rgba(16, 185, 129, 0.2)
--manifold-text:   #34d399
--manifold-border: rgba(16, 185, 129, 0.3)
```

## Responsive Breakpoints

```css
/* Mobile first approach */
@media (min-width: 640px)  { /* sm - tablet */ }
@media (min-width: 768px)  { /* md - desktop */ }
@media (min-width: 1024px) { /* lg - wide desktop */ }
@media (min-width: 1280px) { /* xl - extra wide */ }
```

## Grid System

### Market Grid
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
  {/* Cards */}
</div>
```

### Stats Grid
```tsx
<div className="grid grid-cols-2 gap-3">
  {/* Stats */}
</div>
```

## Z-Index Scale

```css
--z-base:     0
--z-dropdown: 10
--z-sticky:   20
--z-fixed:    30
--z-modal:    40
--z-popover:  50
--z-tooltip:  60
```

## Common Tailwind Patterns

### Glassmorphism Card
```tsx
className="bg-dark-card/60 backdrop-blur-sm"
```

### Hover Glow Effect
```tsx
className="hover:shadow-glow-md transition-shadow"
```

### Gradient Text
```tsx
className="bg-gradient-primary bg-clip-text text-transparent"
```

### Monospace Numbers
```tsx
className="font-mono tabular-nums"
```

### Skeleton Loader
```tsx
className="bg-zinc-800/50 animate-pulse rounded-lg"
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-30
**Maintained By**: UI/UX Team
