# Runtime Profiling

## Chrome DevTools Flame Charts

### Reading a Flame Chart
- **X-axis**: Time (left to right)
- **Y-axis**: Call stack depth (top = entry, bottom = deepest call)
- **Width**: Duration of function call
- **Color**: Yellow = scripting, Purple = layout, Green = paint, Gray = system

### Key Indicators
- **Red corners on tasks**: Long task (>50ms) — blocks main thread
- **Layout (purple bars)**: Forced reflow — check for layout thrashing
- **Recalculate Style**: Usually triggered by DOM changes

### Finding the Bottleneck
1. Record the slow interaction
2. Look for the widest bar at the bottom of the flame chart
3. That's your innermost hot function
4. Check if it's your code or a library

## Memory Profiling

### Heap Snapshot Comparison

```
1. DevTools → Memory → Take heap snapshot (baseline)
2. Perform the suspected leaking action
3. Take another heap snapshot
4. Select snapshot 2, change view to "Comparison"
5. Sort by "# Delta" descending
6. Look for unexpected retained objects
```

### Detecting Memory Leaks

```typescript
// Common leak patterns to check:

// 1. Event listeners not cleaned up
useEffect(() => {
  const handler = () => { /* ... */ };
  window.addEventListener("resize", handler);
  return () => window.removeEventListener("resize", handler); // MUST clean up
}, []);

// 2. Intervals not cleared
useEffect(() => {
  const id = setInterval(() => { /* ... */ }, 1000);
  return () => clearInterval(id);
}, []);

// 3. AbortController for fetch
useEffect(() => {
  const controller = new AbortController();
  fetch("/api/data", { signal: controller.signal })
    .then(r => r.json())
    .then(setData)
    .catch(e => { if (e.name !== "AbortError") throw e; });
  return () => controller.abort();
}, []);

// 4. Closures retaining large objects
function processData(data: HugeObject[]) {
  // BAD: closure retains entire `data` array
  return () => console.log(data.length);

  // GOOD: capture only what's needed
  const len = data.length;
  return () => console.log(len);
}
```

### Runtime Memory Check

```typescript
// DevTools Console
// Check current memory usage
console.log(performance.memory); // Chrome only
// {
//   jsHeapSizeLimit: 2172649472,
//   totalJSHeapSize: 45678592,
//   usedJSHeapSize: 32456789
// }

// Monitor memory over time
setInterval(() => {
  const { usedJSHeapSize } = (performance as any).memory;
  console.log(`Heap: ${(usedJSHeapSize / 1024 / 1024).toFixed(1)}MB`);
}, 5000);
```

## React DevTools Profiler

### Setup
1. Install React DevTools browser extension
2. Open DevTools → Profiler tab
3. Click Record → Interact → Stop

### What to Look For

| Color | Meaning |
|-------|---------|
| Blue/cool | Fast render |
| Yellow/warm | Moderate render |
| Red/hot | Slow render |
| Gray | Did not render |

### Analyzing Render Causes

```
1. Click on a component in the Profiler
2. Check "Why did this render?" section:
   - Props changed
   - State changed
   - Hooks changed
   - Parent rendered
3. For "Parent rendered" → add React.memo()
4. For "Props changed" → check if new references are created
```

### Fixing Unnecessary Renders

```tsx
// Problem: Child re-renders on every parent render
function Parent() {
  const [count, setCount] = useState(0);
  return (
    <>
      <button onClick={() => setCount(c => c + 1)}>+</button>
      <ExpensiveChild data={items} /> {/* re-renders even though items didn't change */}
    </>
  );
}

// Fix 1: React.memo
const ExpensiveChild = memo(function ExpensiveChild({ data }: { data: Item[] }) {
  return <>{/* expensive render */}</>;
});

// Fix 2: useMemo for computed values
function Parent() {
  const [count, setCount] = useState(0);
  const [items, setItems] = useState<Item[]>([]);

  const sortedItems = useMemo(
    () => items.toSorted((a, b) => a.name.localeCompare(b.name)),
    [items]
  );

  return <ExpensiveChild data={sortedItems} />;
}

// Fix 3: useCallback for handlers passed as props
function Parent() {
  const handleClick = useCallback((id: string) => {
    // handle click
  }, []);

  return <ChildList onClick={handleClick} />;
}
```

## Performance Marks API — Custom Instrumentation

```typescript
class PerfTracker {
  static start(label: string) {
    performance.mark(`${label}-start`);
  }

  static end(label: string): number {
    performance.mark(`${label}-end`);
    const measure = performance.measure(label, `${label}-start`, `${label}-end`);
    return measure.duration;
  }

  static async track<T>(label: string, fn: () => Promise<T>): Promise<T> {
    this.start(label);
    try {
      return await fn();
    } finally {
      const duration = this.end(label);
      if (duration > 100) {
        console.warn(`[Perf] ${label}: ${duration.toFixed(1)}ms`);
      }
    }
  }

  static report() {
    const entries = performance.getEntriesByType("measure");
    console.table(
      entries.map((e) => ({
        name: e.name,
        duration: `${e.duration.toFixed(1)}ms`,
        start: `${e.startTime.toFixed(0)}ms`,
      }))
    );
  }
}

// Usage
await PerfTracker.track("fetchUsers", () => fetch("/api/users").then(r => r.json()));
PerfTracker.report();
```

## Layout Thrashing Detection

```typescript
// BAD: read-write-read-write forces multiple reflows
elements.forEach((el) => {
  const height = el.offsetHeight;      // READ (triggers layout)
  el.style.height = height * 2 + "px"; // WRITE (invalidates layout)
});

// GOOD: batch reads, then batch writes
const heights = elements.map((el) => el.offsetHeight); // all READs
elements.forEach((el, i) => {
  el.style.height = heights[i] * 2 + "px";             // all WRITEs
});

// BEST: use requestAnimationFrame
function batchDOMUpdate(elements: HTMLElement[]) {
  // Read phase
  const measurements = elements.map((el) => ({
    el,
    height: el.offsetHeight,
  }));

  // Write phase in next frame
  requestAnimationFrame(() => {
    measurements.forEach(({ el, height }) => {
      el.style.height = height * 2 + "px";
    });
  });
}
```
