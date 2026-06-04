# Dashboard Layout Patterns

## CSS Grid Dashboard

```tsx
function Dashboard() {
  return (
    <div className="grid grid-cols-12 gap-4 p-6">
      {/* KPI Row — 4 cards */}
      <div className="col-span-3"><KPICard title="Revenue" value="$48.2K" change={12.5} /></div>
      <div className="col-span-3"><KPICard title="Users" value="2,847" change={8.3} /></div>
      <div className="col-span-3"><KPICard title="Orders" value="1,234" change={-2.1} /></div>
      <div className="col-span-3"><KPICard title="Conversion" value="3.2%" change={0.5} /></div>

      {/* Main chart — takes 8 cols */}
      <div className="col-span-8">
        <DashboardCard title="Revenue Over Time">
          <RevenueChart data={revenueData} />
        </DashboardCard>
      </div>

      {/* Side chart — 4 cols */}
      <div className="col-span-4">
        <DashboardCard title="Traffic Sources">
          <TrafficDonut data={trafficData} />
        </DashboardCard>
      </div>

      {/* Full width table */}
      <div className="col-span-12">
        <DashboardCard title="Recent Orders">
          <OrdersTable data={ordersData} />
        </DashboardCard>
      </div>
    </div>
  );
}
```

## Responsive Breakpoints

```tsx
function Dashboard() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 lg:p-6">
      {/* KPIs: 1 col mobile, 2 col tablet, 4 col desktop */}
      <KPICard title="Revenue" value="$48.2K" change={12.5} />
      <KPICard title="Users" value="2,847" change={8.3} />
      <KPICard title="Orders" value="1,234" change={-2.1} />
      <KPICard title="Conversion" value="3.2%" change={0.5} />

      {/* Charts: full width mobile, split on desktop */}
      <div className="col-span-1 sm:col-span-2 lg:col-span-3">
        <DashboardCard title="Revenue Over Time">
          <RevenueChart />
        </DashboardCard>
      </div>

      <div className="col-span-1 sm:col-span-2 lg:col-span-1">
        <DashboardCard title="Sources">
          <TrafficDonut />
        </DashboardCard>
      </div>
    </div>
  );
}
```

## KPI Widget

```tsx
interface KPICardProps {
  title: string;
  value: string;
  change: number;      // Percentage change
  icon?: React.ReactNode;
  period?: string;
}

function KPICard({ title, value, change, icon, period = 'vs last month' }: KPICardProps) {
  const isPositive = change >= 0;

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-500">{title}</span>
        {icon && <span className="text-gray-400">{icon}</span>}
      </div>

      <div className="mt-2">
        <span className="text-3xl font-bold text-gray-900">{value}</span>
      </div>

      <div className="mt-2 flex items-center gap-1">
        <span className={`text-sm font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
          {isPositive ? '↑' : '↓'} {Math.abs(change)}%
        </span>
        <span className="text-sm text-gray-400">{period}</span>
      </div>
    </div>
  );
}
```

## Dashboard Card Container

```tsx
interface DashboardCardProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  loading?: boolean;
}

function DashboardCard({ title, subtitle, action, children, loading }: DashboardCardProps) {
  return (
    <div className="rounded-xl border bg-white shadow-sm">
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div>
          <h3 className="text-base font-semibold text-gray-900">{title}</h3>
          {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
        </div>
        {action}
      </div>

      <div className="p-6">
        {loading ? <ChartSkeleton /> : children}
      </div>
    </div>
  );
}
```

## Loading Skeletons

```tsx
function ChartSkeleton({ height = 300 }: { height?: number }) {
  return (
    <div className="animate-pulse" style={{ height }}>
      <div className="flex items-end gap-2 h-full">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="bg-gray-200 rounded-t flex-1"
            style={{ height: `${30 + Math.random() * 60}%` }}
          />
        ))}
      </div>
    </div>
  );
}

function KPISkeleton() {
  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm animate-pulse">
      <div className="h-4 w-20 bg-gray-200 rounded" />
      <div className="h-8 w-28 bg-gray-200 rounded mt-3" />
      <div className="h-4 w-32 bg-gray-200 rounded mt-3" />
    </div>
  );
}

function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="animate-pulse space-y-3">
      <div className="h-8 bg-gray-100 rounded" /> {/* Header */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-12 bg-gray-50 rounded" />
      ))}
    </div>
  );
}
```

## Real-Time Update Pattern

```tsx
import { useQuery } from '@tanstack/react-query';

function LiveDashboard() {
  const { data: kpis, isLoading } = useQuery({
    queryKey: ['dashboard-kpis'],
    queryFn: () => fetch('/api/dashboard/kpis').then((r) => r.json()),
    refetchInterval: 30_000, // Refresh every 30 seconds
  });

  const { data: chartData } = useQuery({
    queryKey: ['dashboard-chart'],
    queryFn: () => fetch('/api/dashboard/chart').then((r) => r.json()),
    refetchInterval: 60_000, // Refresh every minute
  });

  return (
    <div className="grid grid-cols-4 gap-4 p-6">
      {isLoading
        ? Array(4).fill(0).map((_, i) => <KPISkeleton key={i} />)
        : kpis.map((kpi) => <KPICard key={kpi.title} {...kpi} />)
      }
      <div className="col-span-4">
        {chartData ? <RevenueChart data={chartData} /> : <ChartSkeleton />}
      </div>
    </div>
  );
}
```

## Filter Interactions

```tsx
import { useState } from 'react';

type DateRange = '7d' | '30d' | '90d' | '1y' | 'custom';

function DashboardFilters({
  onDateRangeChange,
  onCategoryChange,
}: {
  onDateRangeChange: (range: DateRange) => void;
  onCategoryChange: (categories: string[]) => void;
}) {
  const [dateRange, setDateRange] = useState<DateRange>('30d');

  const ranges: { value: DateRange; label: string }[] = [
    { value: '7d', label: '7 days' },
    { value: '30d', label: '30 days' },
    { value: '90d', label: '90 days' },
    { value: '1y', label: '1 year' },
  ];

  return (
    <div className="flex items-center gap-4 mb-6">
      {/* Date range pills */}
      <div className="flex rounded-lg border bg-gray-50 p-1">
        {ranges.map((range) => (
          <button
            key={range.value}
            onClick={() => {
              setDateRange(range.value);
              onDateRangeChange(range.value);
            }}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              dateRange === range.value
                ? 'bg-white text-gray-900 shadow-sm font-medium'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {range.label}
          </button>
        ))}
      </div>

      {/* Export */}
      <button className="ml-auto px-4 py-2 text-sm border rounded-lg hover:bg-gray-50">
        Export CSV
      </button>
    </div>
  );
}
```

## Sparkline (Inline Mini Chart)

```tsx
import { LineChart, Line, ResponsiveContainer } from 'recharts';

function Sparkline({ data, color = '#4e79a7', height = 40 }: {
  data: number[];
  color?: string;
  height?: number;
}) {
  const chartData = data.map((value, index) => ({ value, index }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData}>
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

// Usage in a table row
function MetricRow({ label, value, trend }: { label: string; value: string; trend: number[] }) {
  return (
    <tr>
      <td className="py-3 text-gray-600">{label}</td>
      <td className="py-3 font-medium">{value}</td>
      <td className="py-3 w-24"><Sparkline data={trend} /></td>
    </tr>
  );
}
```
