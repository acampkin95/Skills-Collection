# Recharts Patterns

## Setup

```bash
npm install recharts
```

## Bar Chart

```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const data = [
  { month: 'Jan', revenue: 4000, expenses: 2400 },
  { month: 'Feb', revenue: 3000, expenses: 1398 },
  { month: 'Mar', revenue: 5000, expenses: 3200 },
  { month: 'Apr', revenue: 4780, expenses: 2908 },
  { month: 'May', revenue: 5890, expenses: 4800 },
  { month: 'Jun', revenue: 6390, expenses: 3800 },
];

function RevenueChart() {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="month" tick={{ fill: '#6b7280' }} />
        <YAxis tick={{ fill: '#6b7280' }} tickFormatter={(v) => `$${v / 1000}k`} />
        <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
        <Legend />
        <Bar dataKey="revenue" fill="#4e79a7" radius={[4, 4, 0, 0]} />
        <Bar dataKey="expenses" fill="#e15759" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

## Custom Bar Shape

```tsx
import { BarChart, Bar, Rectangle, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

// Rounded bar with conditional coloring
function CustomBar(props: any) {
  const { x, y, width, height, value, threshold = 5000 } = props;
  const fill = value >= threshold ? '#59a14f' : '#e15759';
  const radius = 6;

  return (
    <g>
      <defs>
        <linearGradient id={`grad-${value}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={fill} stopOpacity={1} />
          <stop offset="100%" stopColor={fill} stopOpacity={0.6} />
        </linearGradient>
      </defs>
      <rect
        x={x} y={y} width={width} height={height}
        rx={radius} ry={radius}
        fill={`url(#grad-${value})`}
      />
      {/* Value label on top */}
      <text x={x + width / 2} y={y - 8} textAnchor="middle" fill="#374151" fontSize={12}>
        ${(value / 1000).toFixed(1)}k
      </text>
    </g>
  );
}

function CustomBarChart({ data }: { data: Array<{ month: string; revenue: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data}>
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="revenue" shape={<CustomBar />} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

## Line Chart

```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function TrendChart({ data }: { data: Array<{ date: string; users: number; sessions: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="users"
          stroke="#4e79a7"
          strokeWidth={2}
          dot={{ r: 3 }}
          activeDot={{ r: 6 }}
        />
        <Line
          type="monotone"
          dataKey="sessions"
          stroke="#f28e2b"
          strokeWidth={2}
          strokeDasharray="5 5"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

## Pie / Donut Chart

```tsx
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f'];

const data = [
  { name: 'Direct', value: 400 },
  { name: 'Organic', value: 300 },
  { name: 'Referral', value: 200 },
  { name: 'Social', value: 150 },
  { name: 'Email', value: 100 },
];

function TrafficDonut() {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={70}   /* Makes it a donut */
          outerRadius={110}
          paddingAngle={2}
          dataKey="value"
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
        >
          {data.map((_, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value: number) => value.toLocaleString()} />
      </PieChart>
    </ResponsiveContainer>
  );
}
```

## Area Chart

```tsx
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function StackedAreaChart({ data }: { data: Array<{ date: string; mobile: number; desktop: number; tablet: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <AreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Area type="monotone" dataKey="desktop" stackId="1" stroke="#4e79a7" fill="#4e79a7" fillOpacity={0.6} />
        <Area type="monotone" dataKey="mobile" stackId="1" stroke="#f28e2b" fill="#f28e2b" fillOpacity={0.6} />
        <Area type="monotone" dataKey="tablet" stackId="1" stroke="#76b7b2" fill="#76b7b2" fillOpacity={0.6} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
```

## Gradient Fills

```tsx
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, defs } from 'recharts';

function GradientAreaChart({ data }: { data: Array<{ date: string; value: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#4e79a7" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#4e79a7" stopOpacity={0.05} />
          </linearGradient>
          <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#59a14f" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#59a14f" stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Area
          type="monotone"
          dataKey="value"
          stroke="#4e79a7"
          fill="url(#colorValue)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
```

## Custom Tooltip

```tsx
interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>
      {payload.map((entry, index) => (
        <div key={index} className="flex items-center gap-2 text-sm">
          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-gray-600">{entry.name}:</span>
          <span className="font-medium">${entry.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}

// Usage
<Tooltip content={<CustomTooltip />} />
```

## Custom Legend

```tsx
function CustomLegend({ payload }: { payload?: Array<{ value: string; color: string }> }) {
  if (!payload) return null;
  return (
    <div className="flex gap-6 justify-center mt-4">
      {payload.map((entry, index) => (
        <div key={index} className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-sm text-gray-600">{entry.value}</span>
        </div>
      ))}
    </div>
  );
}

// Usage
<Legend content={<CustomLegend />} />
```

## Composed Chart (Bar + Line)

```tsx
import {
  ComposedChart, Bar, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

function ComboChart({ data }: { data: Array<{ month: string; sales: number; growth: number; target: number }> }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis yAxisId="left" />
        <YAxis yAxisId="right" orientation="right" tickFormatter={(v) => `${v}%`} />
        <Tooltip />
        <Legend />
        <Bar yAxisId="left" dataKey="sales" fill="#4e79a7" radius={[4, 4, 0, 0]} />
        <Line yAxisId="right" dataKey="growth" stroke="#e15759" strokeWidth={2} />
        <Line yAxisId="left" dataKey="target" stroke="#76b7b2" strokeDasharray="5 5" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
```

## Synchronized Charts with Brush

```tsx
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Brush, ResponsiveContainer, BarChart, Bar,
} from 'recharts';

function SynchronizedCharts({ data }: { data: Array<{ date: string; revenue: number; orders: number }> }) {
  return (
    <div className="space-y-4">
      {/* Primary chart with Brush control */}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} syncId="dashboard">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="revenue" stroke="#4e79a7" strokeWidth={2} />
          {/* Brush syncs zoom across all charts with same syncId */}
          <Brush dataKey="date" height={30} stroke="#4e79a7" fill="#f3f4f6" />
        </LineChart>
      </ResponsiveContainer>

      {/* Secondary chart — automatically syncs via syncId */}
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} syncId="dashboard">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="orders" fill="#f28e2b" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
```

## Animation Customization

```tsx
// Disable animation for real-time data
<Line isAnimationActive={false} />

// Custom animation timing
<Bar animationDuration={800} animationEasing="ease-in-out" />

// Staggered animation on multiple bars
<Bar animationBegin={0} animationDuration={1500} />
<Bar animationBegin={300} animationDuration={1500} />

// Custom animation with onAnimationEnd callback
<Line
  animationDuration={2000}
  animationEasing="ease-out"
  onAnimationEnd={() => console.log('Chart animation complete')}
/>

// Per-data-point animation with custom active shape
<Pie
  activeShape={(props: any) => {
    const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill } = props;
    return (
      <g>
        <Sector
          cx={cx} cy={cy}
          innerRadius={innerRadius - 5}
          outerRadius={outerRadius + 10}
          startAngle={startAngle}
          endAngle={endAngle}
          fill={fill}
        />
      </g>
    );
  }}
  activeIndex={activeIndex}
/>
```

## Reference Lines & Areas

```tsx
import { ReferenceLine, ReferenceArea } from 'recharts';

// Target line
<ReferenceLine y={5000} stroke="#e15759" strokeDasharray="3 3" label="Target" />

// Today marker
<ReferenceLine x="Mar 15" stroke="#6b7280" label="Today" />

// Highlight a range
<ReferenceArea x1="Jan" x2="Mar" fill="#4e79a7" fillOpacity={0.1} label="Q1" />
```
