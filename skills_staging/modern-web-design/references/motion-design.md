# Motion Design Complete Guide - 2025

## Animation Principles

### Performance-First Rules

**Only animate GPU-accelerated properties:**
- `transform` (translate, scale, rotate)
- `opacity`
- `filter` (blur, brightness)

**Avoid animating:**
- `width`, `height`
- `top`, `left`, `right`, `bottom`
- `margin`, `padding`
- `border-width`
- `font-size`

### Timing Guidelines

| Interaction Type | Duration | Easing |
|-----------------|----------|--------|
| Micro-interactions (hover, focus) | 100-150ms | ease-out |
| Button press/feedback | 100-200ms | ease-out |
| UI element state change | 200-300ms | ease-in-out |
| Modal/dialog open | 200-300ms | ease-out |
| Modal/dialog close | 150-200ms | ease-in |
| Page transitions | 300-500ms | ease-out |
| Stagger delays | 50-100ms | - |
| Complex sequences | 500-1000ms | custom |

### Easing Reference

```css
/* Standard easings */
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* Expressive easings */
--ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
--ease-elastic: cubic-bezier(0.68, -0.55, 0.265, 1.55);
--ease-snap: cubic-bezier(0.7, 0, 0.84, 0);

/* Spring-like */
--ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
```

## View Transitions API (2025 Standard)

The View Transitions API reached Interop 2025 status with cross-browser support, enabling smooth transitions for both SPAs and MPAs.

### Cross-Document Transitions (MPAs)

```css
/* Enable for all same-origin navigations */
@view-transition {
  navigation: auto;
}

/* Default page transition */
::view-transition-old(root) {
  animation: 300ms ease-out both fade-out;
}

::view-transition-new(root) {
  animation: 300ms ease-out both fade-in;
}

@keyframes fade-out {
  to { opacity: 0; }
}

@keyframes fade-in {
  from { opacity: 0; }
}

/* Slide transition */
::view-transition-old(root) {
  animation: 400ms ease-out both slide-out-left;
}

::view-transition-new(root) {
  animation: 400ms ease-out both slide-in-right;
}

@keyframes slide-out-left {
  to { transform: translateX(-100%); opacity: 0; }
}

@keyframes slide-in-right {
  from { transform: translateX(100%); opacity: 0; }
}
```

### Named View Transitions

```css
/* Assign transition names to specific elements */
.hero-image {
  view-transition-name: hero;
}

.page-title {
  view-transition-name: title;
}

.nav-bar {
  view-transition-name: nav;
  /* Nav stays fixed during transition */
}

/* Custom animations per element */
::view-transition-old(hero) {
  animation: 500ms ease-out both scale-down;
}

::view-transition-new(hero) {
  animation: 500ms ease-out both scale-up;
}

@keyframes scale-down {
  to { transform: scale(0.8); opacity: 0; }
}

@keyframes scale-up {
  from { transform: scale(1.2); opacity: 0; }
}

/* Keep nav visible during transition */
::view-transition-group(nav) {
  animation: none;
}
```

### SPA View Transitions (React/Next.js)

```tsx
// hooks/useViewTransition.ts
import { useCallback } from 'react';

export function useViewTransition() {
  const startTransition = useCallback((callback: () => void) => {
    if (!document.startViewTransition) {
      callback();
      return;
    }
    document.startViewTransition(callback);
  }, []);
  
  return { startTransition };
}

// Usage in component
function Navigation() {
  const router = useRouter();
  const { startTransition } = useViewTransition();
  
  const handleNavigation = (href: string) => {
    startTransition(() => {
      router.push(href);
    });
  };
  
  return (
    <nav>
      <button onClick={() => handleNavigation('/about')}>About</button>
      <button onClick={() => handleNavigation('/contact')}>Contact</button>
    </nav>
  );
}
```

```tsx
// With async data loading
function ProductCard({ product }) {
  const router = useRouter();
  
  const handleClick = async () => {
    if (!document.startViewTransition) {
      router.push(`/products/${product.id}`);
      return;
    }
    
    const transition = document.startViewTransition(async () => {
      router.push(`/products/${product.id}`);
      // Wait for new page to render
      await new Promise(resolve => setTimeout(resolve, 100));
    });
    
    await transition.finished;
  };
  
  return (
    <div 
      onClick={handleClick}
      style={{ viewTransitionName: `product-${product.id}` }}
    >
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
    </div>
  );
}
```

## Scroll-Driven Animations (Native CSS)

### Reading Progress Indicator

```css
.progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  transform-origin: left;
  animation: scale-x linear both;
  animation-timeline: scroll();
}

@keyframes scale-x {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}
```

### Reveal on Scroll

```css
.reveal-on-scroll {
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry 25% cover 50%;
}

@keyframes reveal {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Staggered children reveal */
.stagger-container > * {
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry 10% cover 40%;
}

.stagger-container > *:nth-child(1) { animation-delay: 0ms; }
.stagger-container > *:nth-child(2) { animation-delay: 50ms; }
.stagger-container > *:nth-child(3) { animation-delay: 100ms; }
.stagger-container > *:nth-child(4) { animation-delay: 150ms; }
```

### Parallax Effect

```css
.parallax-slow {
  animation: parallax linear;
  animation-timeline: scroll();
}

@keyframes parallax {
  from { transform: translateY(0); }
  to { transform: translateY(-100px); }
}

.parallax-fast {
  animation: parallax-fast linear;
  animation-timeline: scroll();
}

@keyframes parallax-fast {
  from { transform: translateY(0); }
  to { transform: translateY(-200px); }
}
```

### Horizontal Scroll Animation

```css
.horizontal-scroll-container {
  overflow-x: auto;
  scroll-timeline-name: --horizontal-scroll;
  scroll-timeline-axis: x;
}

.scroll-indicator {
  animation: scroll-progress linear;
  animation-timeline: --horizontal-scroll;
}

@keyframes scroll-progress {
  from { width: 0%; }
  to { width: 100%; }
}
```

## CSS Animations

### Transition Patterns

```css
/* Button hover with multiple properties */
.button {
  transition: transform 150ms ease-out, 
              background-color 150ms ease-out,
              box-shadow 150ms ease-out;
}

.button:hover {
  transform: translateY(-2px);
  background-color: var(--primary-hover);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.button:active {
  transform: translateY(0) scale(0.98);
}

/* Card hover effect */
.card {
  transition: transform 200ms ease-out, 
              box-shadow 200ms ease-out;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -8px rgb(0 0 0 / 0.15);
}

/* Link underline animation */
.link {
  position: relative;
}

.link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 250ms ease-out;
}

.link:hover::after {
  transform: scaleX(1);
  transform-origin: left;
}
```

### Keyframe Animations

```css
/* Fade in up */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in-up {
  animation: fadeInUp 400ms ease-out forwards;
}

/* Pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}

/* Spin */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spin {
  animation: spin 1s linear infinite;
}

/* Bounce */
@keyframes bounce {
  0%, 100% {
    transform: translateY(-25%);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}

.bounce {
  animation: bounce 1s infinite;
}

/* Shake */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.shake {
  animation: shake 200ms ease-in-out;
}

/* Skeleton loading */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--muted) 25%,
    var(--muted-foreground) 50%,
    var(--muted) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

## Tailwind CSS v4 Animations

### Built-in Animation Classes

```html
<!-- Spin -->
<svg class="animate-spin h-5 w-5">...</svg>

<!-- Ping (notification dot) -->
<span class="animate-ping absolute h-3 w-3 rounded-full bg-primary"></span>

<!-- Pulse (skeleton) -->
<div class="animate-pulse bg-muted h-4 rounded"></div>

<!-- Bounce -->
<div class="animate-bounce">↓</div>
```

### Custom Tailwind Animations (v4 CSS-first)

```css
@import "tailwindcss";

@theme {
  /* Custom animations */
  --animate-fade-in: fade-in 400ms ease-out;
  --animate-fade-in-up: fade-in-up 400ms ease-out;
  --animate-fade-in-down: fade-in-down 400ms ease-out;
  --animate-slide-in-left: slide-in-left 300ms ease-out;
  --animate-slide-in-right: slide-in-right 300ms ease-out;
  --animate-scale-in: scale-in 200ms ease-out;
  --animate-wiggle: wiggle 200ms ease-in-out;
  
  @keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  @keyframes fade-in-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  @keyframes fade-in-down {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  @keyframes slide-in-left {
    from { transform: translateX(-100%); }
    to { transform: translateX(0); }
  }
  
  @keyframes slide-in-right {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
  }
  
  @keyframes scale-in {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
  }
  
  @keyframes wiggle {
    0%, 100% { transform: rotate(-3deg); }
    50% { transform: rotate(3deg); }
  }
}
```

## Framer Motion

### Basic Animations

```tsx
import { motion } from 'framer-motion';

// Fade in
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
/>

// Fade in with movement
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4, ease: "easeOut" }}
/>

// Exit animation
import { AnimatePresence } from 'framer-motion';

<AnimatePresence>
  {isVisible && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

### Variants Pattern

```tsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: "easeOut",
    },
  },
};

function StaggeredList({ items }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {items.map((item) => (
        <motion.li key={item.id} variants={itemVariants}>
          {item.content}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

### Scroll Animations (Framer Motion)

```tsx
import { motion, useScroll, useTransform } from 'framer-motion';

// Scroll-triggered fade in
function ScrollReveal({ children }) {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });

  const opacity = useTransform(scrollYProgress, [0, 0.3], [0, 1]);
  const y = useTransform(scrollYProgress, [0, 0.3], [50, 0]);

  return (
    <motion.div ref={ref} style={{ opacity, y }}>
      {children}
    </motion.div>
  );
}

// Parallax effect
function Parallax({ children, offset = 50 }) {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], [offset, -offset]);

  return (
    <motion.div ref={ref} style={{ y }}>
      {children}
    </motion.div>
  );
}
```

### Gesture Animations

```tsx
// Hover and tap
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>

// Drag
<motion.div
  drag
  dragConstraints={{ left: 0, right: 300, top: 0, bottom: 300 }}
  dragElastic={0.2}
  whileDrag={{ scale: 1.1 }}
/>

// Drag to dismiss
<motion.div
  drag="x"
  dragConstraints={{ left: 0, right: 0 }}
  onDragEnd={(e, { offset, velocity }) => {
    if (Math.abs(offset.x) > 100 || Math.abs(velocity.x) > 500) {
      onDismiss();
    }
  }}
/>
```

### Spring Animations

```tsx
// Natural spring
<motion.div
  animate={{ x: 100 }}
  transition={{
    type: "spring",
    stiffness: 260,
    damping: 20,
  }}
/>

// Bouncy spring
<motion.div
  animate={{ scale: 1 }}
  initial={{ scale: 0 }}
  transition={{
    type: "spring",
    stiffness: 400,
    damping: 10,
  }}
/>

// Gentle spring
<motion.div
  animate={{ y: 0 }}
  initial={{ y: -100 }}
  transition={{
    type: "spring",
    stiffness: 100,
    damping: 15,
  }}
/>
```

### Layout Animations

```tsx
// Automatic layout animation
<motion.div layout>
  {/* Content that may change size */}
</motion.div>

// Shared layout animation (between routes)
<motion.div layoutId="hero-image">
  <Image src="/hero.jpg" />
</motion.div>

// Layout with specific properties
<motion.div
  layout
  transition={{
    layout: { duration: 0.3, ease: "easeOut" }
  }}
/>
```

## Accessibility: Reduced Motion

### CSS Approach

```css
/* Disable all animations for users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Or use motion-first approach (progressive enhancement) */
@media (prefers-reduced-motion: no-preference) {
  .animated {
    animation: fadeIn 0.5s ease-out;
  }
}
```

### React Hook

```tsx
function usePrefersReducedMotion() {
  const [prefersReduced, setPrefersReduced] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReduced(mediaQuery.matches);

    const handler = (e: MediaQueryListEvent) => setPrefersReduced(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return prefersReduced;
}

// Usage
function AnimatedComponent() {
  const prefersReduced = usePrefersReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: prefersReduced ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: prefersReduced ? 0 : 0.4 }}
    />
  );
}
```

### Framer Motion Approach

```tsx
import { useReducedMotion } from 'framer-motion';

function Component() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      animate={{ x: 100 }}
      transition={{
        duration: shouldReduceMotion ? 0 : 0.3
      }}
    />
  );
}
```

## Performance Checklist

### Do's

- ✅ Only animate `transform` and `opacity`
- ✅ Use `will-change` sparingly on elements that will animate
- ✅ Remove `will-change` after animation completes
- ✅ Use `requestAnimationFrame` for JS animations
- ✅ Respect `prefers-reduced-motion`
- ✅ Test on low-end devices
- ✅ Use native CSS animations when possible
- ✅ Prefer scroll-driven animations (off main thread)

### Don'ts

- ❌ Animate `width`, `height`, `top`, `left`
- ❌ Use `will-change` on too many elements
- ❌ Run multiple simultaneous heavy animations
- ❌ Animate during scroll without throttling
- ❌ Forget to test reduced motion preference
- ❌ Use JavaScript for simple hover effects

### Performance Monitoring

```javascript
// Check for layout thrashing
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.hadRecentInput) continue;
    console.log('Layout shift:', entry.value);
  }
});

observer.observe({ type: 'layout-shift', buffered: true });
```
