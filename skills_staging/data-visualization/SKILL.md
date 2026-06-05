---
name: data-visualization
description: Data Visualization
---

# Data Visualization

**Quick reference:**
- `references/dashboard-layout.md` — Dashboard grids, KPI layouts, responsive patterns
- `references/recharts-patterns.md` — React/Recharts component recipes
- `references/d3-patterns.md` — D3.js integrations and SVG patterns

## Chart Type Selection Guide

| Data Relationship | Chart Type | When to Use |
|-------------------|------------|-------------|
| Comparison | Bar (vertical) | Compare categories (< 12 items) |
| Comparison | Bar (horizontal) | Long category labels, many items |
| Trend over time | Line | Continuous data, multiple series |
| Trend over time | Area | Show volume/magnitude over time |
| Part of whole | Pie / Donut | 2-6 slices, percentages |
| Part of whole | Stacked Bar | Compare composition across groups |
| Distribution | Histogram | Frequency distribution |
| Distribution | Box Plot | Statistical summary, outliers |
| Correlation | Scatter | Two numeric variables |
| Correlation | Bubble | Three numeric variables |
| Hierarchy | Treemap | Nested categories with values |
| Flow | Sankey | Flow between stages |
| Geographic | Choropleth map | Regional data |
| Progress | Gauge / Radial | KPI vs target |
| Multi-variable | Radar / Spider | Compare entities across 3-8 dimensions |
| Density | Heatmap | Two categorical axes with intensity values |

### Decision Tree

```
What are you showing?
├── Change over time
│   ├── Continuous data → Line chart
│   ├── Discrete periods → Bar chart
│   ├── Volume/magnitude → Area chart
│   └── Multiple series with volume → Stacked area
├── Comparison
│   ├── Few items (< 7) → Bar chart (vertical)
│   ├── Many items or long labels → Bar chart (horizontal)
│   ├── Multi-dimension comparison → Radar chart
│   └── Too many to chart → Sorted table with sparklines
├── Part of whole
│   ├── 2-6 parts → Donut chart
│   ├── Parts across groups → Stacked bar (100%)
│   └── Hierarchical parts → Treemap
├── Distribution
│   ├── Single variable → Histogram
│   ├── Compare distributions → Box plot / violin
│   └── Two variables density → Heatmap
├── Relationship / Correlation
│   ├── Two variables → Scatter plot
│   ├── Three variables → Bubble chart
│   └── Many variables → Scatter matrix or parallel coordinates
├── Geographic
│   ├── Regions/countries → Choropleth map
│   └── Points/locations → Dot map
└── Single value / KPI
    ├── vs target → Gauge or bullet chart
    ├── Trend context → KPI card with sparkline
    └── Simple metric → Large number with delta
```

### Data Type → Chart Mapping

| X-Axis Type | Y-Axis Type | Recommended Chart |
|-------------|-------------|-------------------|
| Categorical | Numeric | Bar |
| Time | Numeric | Line / Area |
| Numeric | Numeric | Scatter |
| Categorical | Categorical | Heatmap |
| Hierarchical | Numeric | Treemap |
| None (single) | Numeric | KPI card / Gauge |

## Data Preparation Patterns

### Aggregation

```typescript
// Group and aggregate raw data for charts
function aggregateBy<T>(
  data: T[],
  groupKey: keyof T,
  valueKey: keyof T,
  method: 'sum' | 'avg' | 'count' | 'min' | 'max' = 'sum'
): Array<{ group: string; value: number }> {
  const groups = new Map<string, number[]>();
  for (const item of data) {
    const key = String(item[groupKey]);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(Number(item[valueKey]));
  }

  return Array.from(groups, ([group, values]) => ({
    group,
    value: method === 'sum'   ? values.reduce((a, b) => a + b, 0) :
           method === 'avg'   ? values.reduce((a, b) => a + b, 0) / values.length :
           method === 'count' ? values.length :
           method === 'min'   ? Math.min(...values) :
                                Math.max(...values),
  }));
}
```

### Binning (Histograms)

```typescript
function bin(data: number[], binCount: number): Array<{ range: string; count: number }> {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const binWidth = (max - min) / binCount;

  const bins = Array.from({ length: binCount }, (_, i) => ({
    range: `${(min + i * binWidth).toFixed(1)}-${(min + (i + 1) * binWidth).toFixed(1)}`,
    count: 0,
  }));

  for (const val of data) {
    const idx = Math.min(Math.floor((val - min) / binWidth), binCount - 1);
    bins[idx].count++;
  }
  return bins;
}
```

### Time Series Formatting

```typescript
// Fill gaps in time series data (missing dates get null/0)
function fillTimeSeries(
  data: Array<{ date: string; value: number }>,
  interval: 'day' | 'week' | 'month'
): Array<{ date: string; value: number }> {
  if (!data.length) return [];
  const filled: Array<{ date: string; value: number }> = [];
  const dataMap = new Map(data.map(d => [d.date, d.value]));
  const start = new Date(data[0].date);
  const end = new Date(data[data.length - 1].date);

  for (let d = new Date(start); d <= end; ) {
    const key = d.toISOString().split('T')[0];
    filled.push({ date: key, value: dataMap.get(key) ?? 0 });
    if (interval === 'day') d.setDate(d.getDate() + 1);
    else if (interval === 'week') d.setDate(d.getDate() + 7);
    else d.setMonth(d.getMonth() + 1);
  }
  return filled;
}
```

### Normalization (0-1 or percentage)

```typescript
function normalize(data: number[]): number[] {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  return data.map(v => (v - min) / range);
}

function toPercentOfTotal(values: number[]): number[] {
  const total = values.reduce((a, b) => a + b, 0) || 1;
  return values.map(v => (v / total) * 100);
}
```

## Data Viz Principles

### Perception Principles (Pre-attentive Processing)

Data visualization relies on principles from cognitive science:

- **Position**: Most effective for comparing values (use bar, line charts)
- **Color hue**: Good for categorization, poor for ordering
- **Color saturation/brightness**: Effective for showing intensity/magnitude
- **Size**: Comparisons of area become non-linear (use cautiously)
- **Angle**: Hard to perceive accurately in pie/donut charts
- **Gestalt laws**: Proximity, similarity, continuity group related elements

1. **Data-ink ratio**: Maximize data, minimize decorative elements
2. **Clear labels**: Every axis needs a label with units
3. **Start at zero**: Bar charts must start at zero; line charts may not
4. **Consistent colors**: Same meaning = same color across charts
5. **Sort meaningfully**: Alphabetical, by value, or by logic
6. **Limit categories**: Max 7 colors/series before it becomes confusing
7. **Use whitespace**: Charts need breathing room

## Color Accessibility

### Accessible Color Palettes (Colorblind-Safe)

```typescript
// Okabe-Ito palette (8 colors, designed for colorblind vision)
const OKABE_ITO = [
  '#E69F00', // orange
  '#56B4E9', // sky blue
  '#009E73', // bluish green
  '#F0E442', // yellow
  '#0072B2', // blue
  '#D55E00', // vermillion
  '#CC79A7', // reddish purple
  '#000000', // black
] as const;

// Viridis (perceptually uniform, colorblind-safe, prints in grayscale)
const VIRIDIS = ['#440154', '#3b528b', '#21918c', '#5ec962', '#fde725'];

// Cividis (designed specifically for colorblind viewers)
const CIVIDIS = ['#00204D', '#404E88', '#2E8B57', '#FDB462', '#FFE135'];

// Sequential palette (light to dark — single hue)
const SEQUENTIAL = ['#f7fbff', '#c6dbef', '#6baed6', '#2171b5', '#08306b'];

// Diverging palette (negative to positive)
const DIVERGING = ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#1a9850'];

// Status colors (always pair with icon/pattern, not color alone)
const STATUS = {
  success: '#2e7d32',
  warning: '#ed6c02',
  error:   '#d32f2f',
  info:    '#0288d1',
};
```

### Palette Selection Guide

| Data Type | Palette Type | Example |
|-----------|-------------|---------|
| Categories (nominal) | Categorical (Okabe-Ito) | Product types, regions |
| Ordered low→high | Sequential | Temperature, population density |
| Diverging from center | Diverging | Profit/loss, above/below average |
| Binary good/bad | Two-color | Pass/fail, up/down |

### Rules

- Never use color alone to convey meaning — add patterns, labels, or icons
- Ensure 3:1 contrast ratio for graphical elements (WCAG 2.1 AA)
- Test with colorblindness simulators (Chrome DevTools: Rendering > Emulate vision deficiencies)
- Use Viridis, Cividis, or Okabe-Ito palettes for guaranteed accessibility
- Provide text alternatives: tooltips, data tables, screen reader descriptions

## Accessible Data Visualization

### ARIA for Charts

```tsx
function AccessibleChart({ data, title, description }: Props) {
  return (
    <figure role="img" aria-label={title} aria-describedby="chart-desc">
      <figcaption className="sr-only" id="chart-desc">{description}</figcaption>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data} role="presentation">
          {/* chart content */}
        </BarChart>
      </ResponsiveContainer>
      {/* Data table as fallback for screen readers */}
      <table className="sr-only">
        <caption>{title}</caption>
        <thead><tr><th>Category</th><th>Value</th></tr></thead>
        <tbody>
          {data.map((d) => (
            <tr key={d.name}><td>{d.name}</td><td>{d.value}</td></tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}
```

### Keyboard Navigation for Interactive Charts

```tsx
function KeyboardAccessibleChart({ data }: { data: DataPoint[] }) {
  const [focusedIndex, setFocusedIndex] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowRight': setFocusedIndex(i => Math.min(i + 1, data.length - 1)); break;
      case 'ArrowLeft':  setFocusedIndex(i => Math.max(i - 1, 0)); break;
      case 'Home':       setFocusedIndex(0); break;
      case 'End':        setFocusedIndex(data.length - 1); break;
    }
  };

  return (
    <div
      role="application"
      aria-label="Interactive chart — use arrow keys to navigate data points"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      aria-activedescendant={`point-${focusedIndex}`}
    >
      <p aria-live="polite" className="sr-only">
        {data[focusedIndex].name}: {data[focusedIndex].value}
      </p>
      {/* Chart rendering with visual focus indicator on focusedIndex */}
    </div>
  );
}
```

## Responsive Charts

```tsx
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

function ResponsiveChart({ data }: { data: DataPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#4e79a7" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

### Responsive Breakpoints

```tsx
function useChartDimensions() {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (width < 640) return { tickCount: 3, hideLegend: true, height: 250 };
  if (width < 1024) return { tickCount: 5, hideLegend: false, height: 350 };
  return { tickCount: 10, hideLegend: false, height: 450 };
}
```

## Real-Time Data Updates

```tsx
function RealTimeChart() {
  const [data, setData] = useState<DataPoint[]>([]);
  const MAX_POINTS = 60;

  useEffect(() => {
    const ws = new WebSocket('wss://api.example.com/stream');

    ws.onmessage = (event) => {
      const point = JSON.parse(event.data);
      setData((prev) => {
        const next = [...prev, point];
        return next.length > MAX_POINTS ? next.slice(-MAX_POINTS) : next;
      });
    };

    return () => ws.close();
  }, []);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="time" />
        <YAxis domain={['auto', 'auto']} />
        <Line
          type="monotone"
          dataKey="value"
          stroke="#4e79a7"
          dot={false}
          isAnimationActive={false}  /* Disable animation for real-time */
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

### Incremental Updates with useRef (avoid re-renders)

```tsx
function HighFrequencyChart() {
  const dataRef = useRef<DataPoint[]>([]);
  const chartRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const ws = new WebSocket('wss://api.example.com/fast-stream');
    let animFrame: number;

    ws.onmessage = (event) => {
      const point = JSON.parse(event.data);
      dataRef.current = [...dataRef.current.slice(-199), point];
    };

    // Render loop decoupled from data arrival
    const render = () => {
      drawChart(chartRef.current!, dataRef.current);
      animFrame = requestAnimationFrame(render);
    };
    animFrame = requestAnimationFrame(render);

    return () => { ws.close(); cancelAnimationFrame(animFrame); };
  }, []);

  return <canvas ref={chartRef} width={800} height={400} />;
}
```

## Performance with Large Datasets

**For detailed patterns, see `references/dashboard-layout.md`** — includes:
- Data sampling (LTTB algorithm) for 100K+ points
- Canvas vs SVG decision matrix
- Web Workers for off-main-thread aggregation
- Virtualization with @tanstack/react-virtual
- React ChartJS and Canvas rendering techniques

## Interactive Chart Patterns

**For Recharts interactive examples, see `references/recharts-patterns.md`** — includes:
- Zoom/pan with `<Brush>` component
- Linked/synchronized charts with state management
- Click-through drill-down navigation
- Tooltip and highlight patterns

## Number Formatting

```typescript
// Consistent number display
const formatters = {
  currency: new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }),
  compact:  new Intl.NumberFormat('en-US', { notation: 'compact' }),
  percent:  new Intl.NumberFormat('en-US', { style: 'percent', minimumFractionDigits: 1 }),
  decimal:  new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }),
};

formatters.currency.format(1234567);  // "$1,234,567.00"
formatters.compact.format(1234567);   // "1.2M"
formatters.percent.format(0.1234);    // "12.3%"
```

See references for Recharts component recipes, D3.js patterns and React integration, and dashboard grid/KPI layouts.
