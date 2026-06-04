---
name: data-visualization
description: "Data visualization principles and patterns for non-CLI agents. Covers chart type selection, data preparation concepts, color accessibility, perception principles, and visual design rules. Use when presenting data visually, choosing chart types, designing dashboards, or creating accessible data representations."
version: "1.0.0"
metadata:
  category: data-skills
  scope: non-cli
---

# Data Visualization

Principles, patterns, and decision frameworks for presenting data visually. Covers chart selection, data preparation concepts, accessible color systems, and visual perception rules.

## Chart Type Selection

### Selection Matrix

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

---

## Data Preparation Concepts

### Aggregation Strategies

| Method | When to Use | Effect |
|--------|-------------|--------|
| Sum | Total values per group | Adds all values in group |
| Average | Central tendency per group | Mean of values, susceptible to outliers |
| Median | Central tendency, robust to outliers | Middle value, better for skewed data |
| Count | Frequency analysis | Number of items per group |
| Min/Max | Range analysis | Extreme values per group |

### Binning (For Histograms)

```
PROCESS:
1. Determine data range (min to max)
2. Choose bin count (rule of thumb: √n where n = data points)
3. Calculate bin width: (max - min) / bin_count
4. Assign each data point to its bin
5. Count points per bin

BIN COUNT GUIDANCE:
| Data Points | Recommended Bins |
|-------------|-----------------|
| < 50        | 5-7             |
| 50-200      | 7-10            |
| 200-500     | 10-15           |
| 500+        | 15-22           |
```

### Time Series Handling

| Issue | Solution |
|-------|----------|
| Missing dates | Fill gaps with null or interpolated values |
| Irregular intervals | Resample to regular intervals (day/week/month) |
| Seasonality | Apply moving average for trend isolation |
| Multiple granularities | Provide zoom levels (day → week → month) |

### Normalization

| Technique | Use Case | Formula |
|-----------|----------|---------|
| Min-max (0-1) | Compare different scales | (value - min) / (max - min) |
| Percentage of total | Show proportional contribution | value / total × 100 |
| Z-score | Compare against mean | (value - mean) / std_dev |
| Log transform | Highly skewed distributions | log(value) or log(value + 1) |

---

## Visual Perception Principles

### Pre-attentive Processing

The brain processes these visual properties before conscious thought — use them to highlight data:

| Property | Effective For | Strength |
|----------|--------------|----------|
| **Position** | Comparing values | Strongest — use for primary data |
| **Length** | Comparing magnitude | Strong — basis of bar charts |
| **Color hue** | Categorization | Good for groups, poor for ordering |
| **Color intensity** | Magnitude/heat | Good for continuous values |
| **Size** | Relative comparison | Non-linear perception — use cautiously |
| **Shape** | Categorization | Good for scatter plot differentiation |
| **Angle** | Part-of-whole | Weak — pie charts are hard to read |
| **Area** | Relative magnitude | Very non-linear — perceived as √actual |

### Gestalt Principles in Data Viz

| Principle | Application |
|-----------|-------------|
| **Proximity** | Group related data points physically close together |
| **Similarity** | Use same color/shape for same category across charts |
| **Continuity** | Lines in line charts are naturally perceived as trends |
| **Closure** | Incomplete shapes are mentally completed — use for sparklines |
| **Enclosure** | Box/group related elements with subtle backgrounds |

### Design Rules

1. **Data-ink ratio**: Maximize data, minimize decorative elements
2. **Clear labels**: Every axis needs a label with units
3. **Start at zero**: Bar charts must start at zero; line charts may not
4. **Consistent colors**: Same meaning = same color across charts
5. **Sort meaningfully**: Alphabetical, by value, or by logic — never random
6. **Limit categories**: Max 7 colors/series before it becomes confusing
7. **Use whitespace**: Charts need breathing room for readability

---

## Color Accessibility

### Accessible Color Palettes

**Okabe-Ito (8 colors, colorblind-safe):**
```
#E69F00 (orange),  #56B4E9 (sky blue),  #009E73 (bluish green),
#F0E442 (yellow),  #0072B2 (blue),      #D55E00 (vermillion),
#CC79A7 (reddish purple), #000000 (black)
```

**Viridis (perceptually uniform, grayscale-safe):**
```
#440154 → #3b528b → #21918c → #5ec962 → #fde725
```

**Cividis (designed for colorblind viewers):**
```
#00204D → #404E88 → #2E8B57 → #FDB462 → #FFE135
```

**Sequential (light to dark — single hue):**
```
#f7fbff → #c6dbef → #6baed6 → #2171b5 → #08306b
```

**Diverging (negative to positive):**
```
#d73027 → #fc8d59 → #fee08b → #d9ef8b → #1a9850
```

**Status colors (always pair with icon/pattern):**
```
Success: #2e7d32    Warning: #ed6c02
Error:   #d32f2f    Info:    #0288d1
```

### Palette Selection Guide

| Data Type | Palette Type | Example Use |
|-----------|-------------|-------------|
| Categories (nominal) | Categorical (Okabe-Ito) | Product types, regions |
| Ordered low→high | Sequential | Temperature, population density |
| Diverging from center | Diverging | Profit/loss, above/below average |
| Binary good/bad | Two-color | Pass/fail, up/down |

### Accessibility Rules

- Never use color alone — add patterns, labels, or icons
- Ensure 3:1 contrast ratio for graphical elements (WCAG 2.1 AA)
- Provide text alternatives: tooltips, data tables, descriptive summaries
- Test with colorblindness simulators
- Prefer Viridis, Cividis, or Okabe-Ito for guaranteed accessibility

---

## Accessibility Patterns

### Chart Description Template

```
CHART: [chart type]
TITLE: [chart title]
X-AXIS: [label and unit]
Y-AXIS: [label and unit]
DATA SUMMARY: [key takeaway in 1-2 sentences]
TREND: [direction and magnitude]
NOTABLE: [any outliers, peaks, or anomalies]
DATA TABLE: [provide underlying data as text for screen readers]
```

### Responsive Design Breakpoints

| Viewport | Adjustments |
|----------|-------------|
| Mobile (< 640px) | Fewer tick marks, hide legend, height 250px, stack charts vertically |
| Tablet (640-1024px) | Show legend, height 350px, 2-column grid |
| Desktop (> 1024px) | Full tick marks, height 450px, multi-column grid |

---

## Number Formatting

| Format | Use Case | Example |
|--------|----------|---------|
| Currency | Financial data | $1,234,567.00 |
| Compact | Large numbers | 1.2M, 3.4K |
| Percentage | Ratios, growth | 12.3% |
| Decimal | Precise values | 3.14 |
| Scientific | Very large/small | 1.23 × 10⁶ |

### Formatting Rules

- Use consistent decimal places across a chart (2 is standard)
- Add units to axis labels, not to every data point
- Use compact notation when values span orders of magnitude
- Show negative values with explicit minus sign and/or red color
- Round to meaningful precision — don't show 7 decimal places for estimates

---

## Common Mistakes

| Mistake | Why It's Wrong | Fix |
|---------|---------------|-----|
| 3D bar/pie charts | Distorts proportions, harder to read | Use flat 2D charts |
| Dual Y-axes | Misleading correlation impression | Use separate charts or normalize |
| Rainbow color scales | Not perceptually uniform, colorblind-unfriendly | Use Viridis or sequential palette |
| Truncated Y-axis on bars | Exaggerates differences | Start bars at zero |
| Too many pie slices | Unreadable beyond 5-6 slices | Use bar chart instead |
| Missing axis labels | Reader can't interpret values | Label every axis with units |
| Grid lines too prominent | Competes with data for attention | Use light, thin grid lines |

## When to Use

- Choosing the right chart type for a dataset
- Designing dashboards or data presentations
- Making visualizations accessible to all users
- Evaluating or critiquing existing data visualizations
- Preparing data for visual representation
- Creating reports with data-driven insights

## Limitations

- No code execution — patterns are conceptual guidance
- Specific rendering implementations (D3, Recharts, etc.) not covered
- Geographic and 3D visualization require specialized tools beyond this scope
- Real-time streaming visualization patterns require framework-specific implementation
- Print-specific considerations (grayscale, page size) not fully covered

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [visual-design](../visual-design/SKILL.md) | Color theory and typography principles apply to chart design |
| [accessibility-knowledge](../accessibility-knowledge/SKILL.md) | WCAG compliance for chart components and descriptions |
| [data-synthesis](../data-synthesis/SKILL.md) | Synthesize findings before visualizing them |
| [reporting](../reporting/SKILL.md) | Charts are key components of reports and dashboards |
| [regex-text-processing](../regex-text-processing/SKILL.md) | Clean and normalize data before visualization |
| [data-visualization](/home/alex/.claude/skills/data-visualization/SKILL.md) | General-purpose data visualization patterns for reports |
