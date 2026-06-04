---
name: data-visualization
description: Data visualization with Recharts, D3.js, and dashboard UI patterns. Use for chart selection, responsive layouts, and KPI dashboards.
version: 2.0.0
reviewed: "2026-06-04"
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

See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.