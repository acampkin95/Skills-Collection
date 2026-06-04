# Creative UI Patterns

## Design Philosophy

**Rule #1:** Commit to a direction. Bold maximalism OR refined minimalism - never the middle ground.

**Rule #2:** Every design decision should be intentional. Ask "why this choice?" for fonts, colors, spacing, and effects.

**Rule #3:** Create memorable moments. One unforgettable element beats ten forgettable ones.

## Anti-Patterns to Avoid

### Generic AI Aesthetics
- Purple/blue gradients on white backgrounds
- Inter, Roboto, Arial, system fonts
- Evenly distributed, timid color palettes
- Predictable card grids with rounded corners
- Stock motion (fade-in everything equally)

### The "Safe" Trap
- Using the same fonts across projects
- Defaulting to `rounded-lg` on everything
- `bg-white` with `shadow-sm` cards
- `gap-4` uniform spacing everywhere

## Bold Typography

### Font Pairing Strategy

**Display + Body combinations:**
```css
@theme {
  /* Dramatic contrast */
  --font-display: "Playfair Display", serif;
  --font-body: "Inter", sans-serif;
  
  /* Modern edge */
  --font-display: "Space Grotesk", sans-serif;
  --font-body: "IBM Plex Sans", sans-serif;
  
  /* Warm personality */
  --font-display: "Fraunces", serif;
  --font-body: "Source Sans 3", sans-serif;
  
  /* Tech forward */
  --font-display: "Syne", sans-serif;
  --font-body: "Outfit", sans-serif;
}
```

### Type Scale with Drama

```tsx
// Massive display with tight tracking
<h1 className="font-display text-[clamp(3rem,8vw,8rem)] leading-[0.9] tracking-[-0.04em]">
  Break<br />Convention
</h1>

// Contrasting subtitle
<p className="font-body text-xl tracking-wide text-foreground/60 mt-6">
  Discover what's possible when you stop playing safe
</p>
```

## Color Strategies

### Dominant + Accent

```css
@theme {
  /* Dark dominant with electric accent */
  --color-bg: #0a0a0a;
  --color-fg: #fafafa;
  --color-accent: #22d3ee;  /* cyan-400 */
  
  /* Warm cream with bold orange */
  --color-bg: #fef7ed;
  --color-fg: #1c1917;
  --color-accent: #f97316;
  
  /* Deep navy with gold */
  --color-bg: #0f172a;
  --color-fg: #f8fafc;
  --color-accent: #fbbf24;
}
```

### Bold Color Blocking

```tsx
<section className="grid lg:grid-cols-2 min-h-screen">
  {/* Solid color block */}
  <div className="bg-amber-400 p-12 flex items-center">
    <h2 className="text-6xl font-bold text-amber-950">
      Make a statement
    </h2>
  </div>
  
  {/* Contrasting content */}
  <div className="bg-slate-950 p-12 flex items-center">
    <p className="text-xl text-slate-300">
      Content that demands attention
    </p>
  </div>
</section>
```

## Spatial Composition

### Breaking the Grid

```tsx
// Overlapping elements
<div className="relative">
  <div className="w-[60%] aspect-square bg-violet-500" />
  <div className="absolute top-1/4 right-0 w-[50%] aspect-[4/3] bg-amber-400 -translate-y-8" />
  <h2 className="absolute bottom-0 left-0 text-8xl font-bold text-white mix-blend-difference">
    Overlap
  </h2>
</div>

// Asymmetric grid
<div className="grid grid-cols-12 gap-4">
  <div className="col-span-7 row-span-2 bg-slate-900" />
  <div className="col-span-5 bg-amber-400" />
  <div className="col-span-3 bg-violet-500" />
  <div className="col-span-2 bg-cyan-400" />
</div>

// Off-grid positioning
<div className="relative">
  <img className="w-[80%] ml-auto" src="hero.jpg" />
  <div className="absolute -left-8 top-1/3 max-w-md bg-white p-8 shadow-2xl">
    <h3 className="text-3xl font-bold">Breaking boundaries</h3>
  </div>
</div>
```

### Dramatic White Space

```tsx
// Hero with breathing room
<section className="min-h-screen flex items-end pb-24 px-8">
  <div className="max-w-2xl">
    <span className="text-sm tracking-[0.3em] uppercase text-foreground/50">
      Collection 2024
    </span>
    <h1 className="text-7xl font-display mt-4 leading-none">
      Minimal
      <br />
      Maximal
    </h1>
  </div>
</section>
```

## Motion & Animation

### Orchestrated Page Load

```tsx
// Staggered reveal
<div className="space-y-4">
  {items.map((item, i) => (
    <div
      key={item.id}
      className="animate-slide-up opacity-0"
      style={{ animationDelay: `${i * 100}ms`, animationFillMode: 'forwards' }}
    >
      {item.content}
    </div>
  ))}
</div>

// CSS keyframes
@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slide-up 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
```

### Surprising Hover States

```tsx
// Scale with color shift
<button className="group relative overflow-hidden bg-slate-900 px-8 py-4">
  <span className="relative z-10 text-white transition-colors group-hover:text-slate-900">
    Explore
  </span>
  <div className="absolute inset-0 bg-amber-400 translate-y-full transition-transform duration-300 group-hover:translate-y-0" />
</button>

// Text scramble effect (use Framer Motion)
<motion.span
  className="inline-block"
  whileHover={{ skewX: -10, transition: { duration: 0.2 } }}
>
  Hover me
</motion.span>

// Border draw
<a className="relative px-6 py-3 group">
  <span>Learn more</span>
  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-current transition-all duration-300 group-hover:w-full" />
</a>
```

### Scroll-Triggered Effects

```tsx
// Using Intersection Observer
'use client'
import { useRef, useEffect, useState } from 'react'

function RevealOnScroll({ children }) {
  const ref = useRef(null)
  const [isVisible, setIsVisible] = useState(false)
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => entry.isIntersecting && setIsVisible(true),
      { threshold: 0.1, rootMargin: '-50px' }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])
  
  return (
    <div
      ref={ref}
      className={cn(
        'transition-all duration-700',
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      )}
    >
      {children}
    </div>
  )
}
```

## Texture & Depth

### Noise Overlay

```tsx
<div className="relative bg-slate-900">
  {/* Content */}
  <div className="relative z-10">{children}</div>
  
  {/* Noise texture */}
  <div 
    className="absolute inset-0 opacity-[0.03] pointer-events-none"
    style={{
      backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
    }}
  />
</div>
```

### Gradient Mesh

```tsx
<div className="relative overflow-hidden bg-slate-950">
  {/* Mesh gradients */}
  <div className="absolute top-0 -left-1/4 w-1/2 aspect-square rounded-full bg-violet-500/30 blur-[100px]" />
  <div className="absolute bottom-0 -right-1/4 w-1/2 aspect-square rounded-full bg-cyan-500/30 blur-[100px]" />
  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1/3 aspect-square rounded-full bg-amber-500/20 blur-[80px]" />
  
  {/* Content */}
  <div className="relative z-10">{children}</div>
</div>
```

### Glass Morphism (Use Sparingly)

```tsx
<div className="relative">
  {/* Background with content */}
  <div className="bg-gradient-to-br from-violet-500 to-cyan-500 p-12">
    <img src="..." className="w-full" />
  </div>
  
  {/* Glass card */}
  <div className="absolute bottom-8 left-8 right-8 backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-6">
    <h3 className="text-white text-xl font-semibold">Glass effect</h3>
  </div>
</div>
```

## Component Examples

### Bold Hero

```tsx
export function Hero() {
  return (
    <section className="relative min-h-screen bg-slate-950 overflow-hidden">
      {/* Background elements */}
      <div className="absolute top-0 right-0 w-1/2 h-full bg-amber-400 clip-diagonal" />
      
      {/* Content */}
      <div className="relative z-10 container mx-auto px-8 py-24 min-h-screen flex flex-col justify-end">
        <span className="text-amber-400 text-sm tracking-[0.2em] uppercase mb-4">
          Introducing
        </span>
        <h1 className="text-white text-[clamp(3rem,10vw,10rem)] font-display leading-[0.85] tracking-tight">
          Bold
          <br />
          <span className="text-amber-400">Vision</span>
        </h1>
        <p className="text-slate-400 text-xl max-w-md mt-8">
          Design that refuses to blend in. Experiences that demand attention.
        </p>
      </div>
    </section>
  )
}

// CSS for diagonal clip
.clip-diagonal {
  clip-path: polygon(30% 0, 100% 0, 100% 100%, 0 100%);
}
```

### Feature Grid

```tsx
export function Features() {
  return (
    <section className="bg-slate-100 py-24">
      <div className="container mx-auto px-8">
        <div className="grid md:grid-cols-3 gap-px bg-slate-300">
          {features.map((feature, i) => (
            <div 
              key={i}
              className={cn(
                "bg-slate-100 p-12 group cursor-pointer transition-colors hover:bg-slate-950",
                i === 1 && "md:col-span-2 md:row-span-2"  // Feature one large
              )}
            >
              <span className="text-6xl mb-6 block group-hover:scale-110 transition-transform">
                {feature.emoji}
              </span>
              <h3 className="text-2xl font-bold group-hover:text-white transition-colors">
                {feature.title}
              </h3>
              <p className="text-slate-600 mt-2 group-hover:text-slate-400 transition-colors">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

### Dramatic Testimonial

```tsx
export function Testimonial() {
  return (
    <section className="bg-slate-950 py-32">
      <div className="container mx-auto px-8">
        <blockquote className="relative">
          {/* Giant quote mark */}
          <span className="absolute -top-16 -left-4 text-[20rem] leading-none text-slate-800 font-serif select-none">
            "
          </span>
          
          <p className="relative z-10 text-white text-4xl md:text-6xl font-display leading-tight max-w-4xl">
            This changed everything about how we approach design.
          </p>
          
          <footer className="mt-12 flex items-center gap-4">
            <img 
              src="/avatar.jpg" 
              className="w-16 h-16 rounded-full ring-4 ring-amber-400"
            />
            <div>
              <cite className="text-white font-semibold not-italic">
                Sarah Chen
              </cite>
              <p className="text-slate-500">Design Director, Acme Inc</p>
            </div>
          </footer>
        </blockquote>
      </div>
    </section>
  )
}
```

## Quick Reference

### Distinctive Font Stacks

```css
/* Editorial */
font-family: "Playfair Display", "Georgia", serif;

/* Modern Sans */
font-family: "Syne", "Helvetica Neue", sans-serif;

/* Tech */
font-family: "Space Grotesk", "SF Pro", sans-serif;

/* Warm */
font-family: "Fraunces", "Charter", serif;

/* Geometric */
font-family: "Outfit", "Avenir", sans-serif;
```

### Impact Colors

```css
/* Electric */
--accent: #22d3ee; /* cyan-400 */
--accent: #a855f7; /* purple-500 */
--accent: #f43f5e; /* rose-500 */

/* Warm */
--accent: #f97316; /* orange-500 */
--accent: #fbbf24; /* amber-400 */
--accent: #84cc16; /* lime-500 */

/* Sophisticated */
--accent: #0ea5e9; /* sky-500 */
--accent: #14b8a6; /* teal-500 */
--accent: #8b5cf6; /* violet-500 */
```
