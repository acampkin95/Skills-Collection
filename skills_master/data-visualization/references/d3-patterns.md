# D3.js Patterns

## Core Concepts

### Scales

```typescript
import * as d3 from 'd3';

// Linear scale (continuous → continuous)
const xScale = d3.scaleLinear()
  .domain([0, 100])       // Data range
  .range([0, 800]);       // Pixel range

xScale(50); // 400

// Band scale (categorical → continuous) — for bar charts
const xBand = d3.scaleBand()
  .domain(['A', 'B', 'C', 'D'])
  .range([0, 800])
  .padding(0.2);

xBand('B');             // x position
xBand.bandwidth();      // bar width

// Time scale
const timeScale = d3.scaleTime()
  .domain([new Date('2025-01-01'), new Date('2025-12-31')])
  .range([0, 800]);

// Color scale (sequential)
const colorScale = d3.scaleSequential(d3.interpolateBlues)
  .domain([0, 100]);

colorScale(75); // Returns a blue color

// Color scale (categorical)
const catColor = d3.scaleOrdinal(d3.schemeTableau10);
catColor('Category A'); // Returns a distinct color

// Log scale
const logScale = d3.scaleLog()
  .domain([1, 1000000])
  .range([0, 600]);
```

### Axes

```typescript
// Create axes
const xAxis = d3.axisBottom(xScale)
  .ticks(5)
  .tickFormat(d3.format(',.0f'));

const yAxis = d3.axisLeft(yScale)
  .ticks(8)
  .tickFormat((d) => `$${d}`);

// Render axes
svg.append('g')
  .attr('class', 'x-axis')
  .attr('transform', `translate(0, ${height})`)
  .call(xAxis);

svg.append('g')
  .attr('class', 'y-axis')
  .call(yAxis);

// Style axes
svg.selectAll('.x-axis .tick text')
  .attr('fill', '#6b7280')
  .attr('font-size', '12px');

// Time axis
const timeAxis = d3.axisBottom(timeScale)
  .ticks(d3.timeMonth.every(1))
  .tickFormat(d3.timeFormat('%b %Y'));
```

### Selections & Data Joins

```typescript
// Select and modify
d3.select('#chart')
  .append('svg')
  .attr('width', 800)
  .attr('height', 400);

// Data join pattern (D3 v7+)
const bars = svg.selectAll('rect')
  .data(data, (d) => d.id)  // Key function for identity
  .join(
    (enter) => enter.append('rect')
      .attr('x', (d) => xScale(d.category))
      .attr('y', height)
      .attr('width', xScale.bandwidth())
      .attr('height', 0)
      .attr('fill', '#4e79a7')
      .call((enter) => enter.transition().duration(750)
        .attr('y', (d) => yScale(d.value))
        .attr('height', (d) => height - yScale(d.value))
      ),
    (update) => update
      .call((update) => update.transition().duration(750)
        .attr('y', (d) => yScale(d.value))
        .attr('height', (d) => height - yScale(d.value))
      ),
    (exit) => exit
      .call((exit) => exit.transition().duration(300)
        .attr('height', 0)
        .attr('y', height)
        .remove()
      )
  );
```

### Transitions

```typescript
// Basic transition
d3.select('circle')
  .transition()
  .duration(750)
  .ease(d3.easeCubicInOut)
  .attr('cx', 400)
  .attr('r', 20)
  .attr('fill', 'steelblue');

// Chained transitions
d3.select('rect')
  .transition()
  .duration(500)
  .attr('width', 200)
  .transition()
  .duration(500)
  .attr('fill', 'red');

// Staggered transitions
svg.selectAll('rect')
  .data(data)
  .join('rect')
  .attr('height', 0)
  .transition()
  .delay((d, i) => i * 100)  // Stagger by 100ms each
  .duration(500)
  .attr('height', (d) => yScale(d.value));
```

## Force-Directed Graph

```typescript
interface Node {
  id: string;
  group: number;
  x?: number;
  y?: number;
}

interface Link {
  source: string;
  target: string;
  value: number;
}

function createForceGraph(nodes: Node[], links: Link[], container: SVGSVGElement) {
  const width = 800;
  const height = 600;

  const svg = d3.select(container)
    .attr('viewBox', [0, 0, width, height]);

  const color = d3.scaleOrdinal(d3.schemeTableau10);

  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id((d: any) => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(20));

  // Links
  const link = svg.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke', '#999')
    .attr('stroke-opacity', 0.6)
    .attr('stroke-width', (d) => Math.sqrt(d.value));

  // Nodes
  const node = svg.append('g')
    .selectAll('circle')
    .data(nodes)
    .join('circle')
    .attr('r', 8)
    .attr('fill', (d) => color(String(d.group)))
    .call(drag(simulation));

  // Labels
  const label = svg.append('g')
    .selectAll('text')
    .data(nodes)
    .join('text')
    .text((d) => d.id)
    .attr('font-size', '10px')
    .attr('dx', 12)
    .attr('dy', 4);

  // Tick handler
  simulation.on('tick', () => {
    link
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y);

    node
      .attr('cx', (d: any) => d.x)
      .attr('cy', (d: any) => d.y);

    label
      .attr('x', (d: any) => d.x)
      .attr('y', (d: any) => d.y);
  });
}

// Drag behavior
function drag(simulation: d3.Simulation<any, any>) {
  return d3.drag<SVGCircleElement, Node>()
    .on('start', (event) => {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    })
    .on('drag', (event) => {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    })
    .on('end', (event) => {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    });
}
```

## D3 with React

### Using useRef + useEffect

```tsx
import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

interface BarChartProps {
  data: Array<{ label: string; value: number }>;
  width?: number;
  height?: number;
}

function D3BarChart({ data, width = 600, height = 400 }: BarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.length) return;

    const margin = { top: 20, right: 20, bottom: 40, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous render

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand()
      .domain(data.map((d) => d.label))
      .range([0, innerWidth])
      .padding(0.2);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, (d) => d.value) || 0])
      .nice()
      .range([innerHeight, 0]);

    // Axes
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x));

    g.append('g').call(d3.axisLeft(y));

    // Bars with animation
    g.selectAll('rect')
      .data(data)
      .join('rect')
      .attr('x', (d) => x(d.label)!)
      .attr('width', x.bandwidth())
      .attr('y', innerHeight)
      .attr('height', 0)
      .attr('fill', '#4e79a7')
      .attr('rx', 4)
      .transition()
      .duration(750)
      .delay((_, i) => i * 100)
      .attr('y', (d) => y(d.value))
      .attr('height', (d) => innerHeight - y(d.value));
  }, [data, width, height]);

  return <svg ref={svgRef} width={width} height={height} />;
}
```

### React for DOM, D3 for Math

```tsx
// Better pattern: Let React handle DOM, D3 handles scales/math only
function ReactD3Chart({ data, width = 600, height = 400 }) {
  const margin = { top: 20, right: 20, bottom: 40, left: 60 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const x = d3.scaleBand()
    .domain(data.map((d) => d.label))
    .range([0, innerW])
    .padding(0.2);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, (d) => d.value) || 0])
    .nice()
    .range([innerH, 0]);

  return (
    <svg width={width} height={height}>
      <g transform={`translate(${margin.left},${margin.top})`}>
        {/* Bars rendered by React */}
        {data.map((d) => (
          <rect
            key={d.label}
            x={x(d.label)}
            y={y(d.value)}
            width={x.bandwidth()}
            height={innerH - y(d.value)}
            fill="#4e79a7"
            rx={4}
          />
        ))}

        {/* X Axis labels */}
        {data.map((d) => (
          <text
            key={d.label}
            x={(x(d.label) || 0) + x.bandwidth() / 2}
            y={innerH + 20}
            textAnchor="middle"
            fontSize={12}
            fill="#6b7280"
          >
            {d.label}
          </text>
        ))}

        {/* Y Axis labels */}
        {y.ticks(5).map((tick) => (
          <g key={tick} transform={`translate(0, ${y(tick)})`}>
            <line x2={innerW} stroke="#e5e7eb" />
            <text x={-10} dy="0.32em" textAnchor="end" fontSize={12} fill="#6b7280">
              {tick}
            </text>
          </g>
        ))}
      </g>
    </svg>
  );
}
```
