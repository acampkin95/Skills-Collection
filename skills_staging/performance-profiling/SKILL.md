---
name: performance-profiling
description: Web performance profiling and Core Web Vitals optimization.
---

# Performance Profiling

## Core Web Vitals (2026 Thresholds — Unchanged from 2024)

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| **INP** (Interaction to Next Paint) | ≤ 200ms | ≤ 500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 |

**Feb 2026 Note:** These thresholds remain stable. Focus on achieving "Good" for SEO ranking benefits and user experience.

## Measuring Web Vitals

```typescript
// lib/web-vitals.ts
import { onLCP, onINP, onCLS, onFCP, onTTFB } from "web-vitals";

function sendToAnalytics(metric: { name: string; value: number; id: string }) {
  // Send to your analytics endpoint
  navigator.sendBeacon("/api/vitals", JSON.stringify(metric));
}

onLCP(sendToAnalytics);
onINP(sendToAnalytics);
onCLS(sendToAnalytics);
onFCP(sendToAnalytics);
onTTFB(sendToAnalytics);
```

## React Profiler — Finding Unnecessary Renders

```tsx
import { Profiler, ProfilerOnRenderCallback } from "react";

const onRender: ProfilerOnRenderCallback = (
  id,           // component tree id
  phase,        // "mount" | "update" | "nested-update"
  actualDuration,   // ms spent rendering
  baseDuration,     // ms for full re-render without memo
  startTime,
  commitTime,
) => {
  if (actualDuration > 16) {
    // over one frame budget
    console.warn(`Slow render: ${id} took ${actualDuration.toFixed(1)}ms (${phase})`);
  }
};

export default function App() {
  return (
    <Profiler id="App" onRender={onRender}>
      <Dashboard />
    </Profiler>
  );
}
```

## Performance Budget

```json
// performance-budget.json
{
  "bundles": {
    "main": { "maxSize": "150kb" },
    "vendor": { "maxSize": "200kb" },
    "total": { "maxSize": "400kb" }
  },
  "vitals": {
    "LCP": 2500,
    "INP": 200,
    "CLS": 0.1,
    "FCP": 1800,
    "TTFB": 800
  },
  "resources": {
    "maxRequests": 50,
    "maxFonts": 3,
    "maxImages": 20
  }
}
```

## Chrome DevTools Performance Panel

### Recording Steps
1. Open DevTools → Performance tab
2. Click Record (or Cmd+Shift+E)
3. Perform the interaction to profile
4. Stop recording
5. Analyze the flame chart

### What to Look For

| Section | Check For |
|---------|-----------|
| **Main thread** | Long tasks (>50ms, red corners) |
| **Network** | Render-blocking resources, waterfall gaps |
| **Frames** | Dropped frames (red bars) |
| **Layout** | Forced reflows / layout thrashing |
| **Timings** | LCP, FCP markers |

### Identifying Long Tasks

```typescript
// Detect long tasks at runtime
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.duration > 50) {
      console.warn("Long task detected:", {
        duration: entry.duration,
        startTime: entry.startTime,
        name: entry.name,
      });
    }
  }
});
observer.observe({ type: "longtask", buffered: true });
```

## Performance Marks and Measures

```typescript
// Mark key user interactions
performance.mark("search-start");

const results = await fetchSearchResults(query);
renderResults(results);

performance.mark("search-end");
performance.measure("search-duration", "search-start", "search-end");

const [measure] = performance.getEntriesByName("search-duration");
console.log(`Search took ${measure.duration.toFixed(0)}ms`);
```

## Common Performance Anti-Patterns

| Anti-Pattern | Impact | Fix |
|-------------|--------|-----|
| Layout thrashing | High INP | Batch DOM reads, then writes |
| Unoptimized images | High LCP | Use `<img>` with width/height, modern formats |
| Render-blocking CSS | High LCP | Inline critical CSS, async load rest |
| No code splitting | High LCP | Dynamic `import()`, route-based splitting |
| Missing `key` prop | High INP | Stable, unique keys in React lists |
| Inline functions in JSX | Moderate | `useCallback` for expensive children |
| Large dependency | High bundle | Bundle analyze + replace or tree-shake |
| No font `display` | CLS | `font-display: swap` or `optional` |
| Unthrottled listeners | High INP | `requestAnimationFrame` or debounce |

## Quick Diagnostic Script

```typescript
// Paste in DevTools Console
(() => {
  // Check LCP element
  new PerformanceObserver((list) => {
    const entries = list.getEntries();
    const last = entries[entries.length - 1];
    console.log("LCP:", last.startTime.toFixed(0) + "ms", last.element);
  }).observe({ type: "largest-contentful-paint", buffered: true });

  // Check CLS
  let clsValue = 0;
  new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      if (!entry.hadRecentInput) {
        clsValue += entry.value;
      }
    }
    console.log("CLS so far:", clsValue.toFixed(4));
  }).observe({ type: "layout-shift", buffered: true });

  // Resource summary
  const resources = performance.getEntriesByType("resource");
  const byType: Record<string, { count: number; size: number }> = {};
  resources.forEach((r) => {
    const ext = r.name.split(".").pop()?.split("?")[0] || "other";
    if (!byType[ext]) byType[ext] = { count: 0, size: 0 };
    byType[ext].count++;
    byType[ext].size += r.transferSize || 0;
  });
  console.table(byType);
})();
```

## References

- [Bundle optimization](references/bundle-optimization.md) — analyzers, tree shaking, code splitting, lazy loading
- [Runtime profiling](references/runtime-profiling.md) — flame graphs, memory, heap snapshots, React DevTools
- [Next.js performance](references/nextjs-performance.md) — ISR, PPR, streaming, Image/Font/Script optimization
