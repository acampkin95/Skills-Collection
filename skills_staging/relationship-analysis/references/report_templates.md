# Report Templates Reference

## HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relationship Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>/* Dark theme styles */</style>
</head>
<body>
    <header><!-- Title, date --></header>
    <nav><!-- Section navigation --></nav>
    <div class="container">
        <section id="dashboard"><!-- Overview stats --></section>
        <section id="timeline"><!-- Temporal analysis --></section>
        <!-- Additional sections -->
    </div>
    <script>
        const DATA = {/* Injected JSON */};
        // Chart initializations
    </script>
</body>
</html>
```

## Report Sections

### 1. Dashboard
- Total messages, words, date range
- Per-sender statistics
- Monthly volume chart
- Hourly distribution chart

### 2. Timeline
- Love:Negative ratio over time
- Monthly love words
- Monthly negative words
- Phase identification

### 3. Sentiment
- Polarity over time (per sender)
- Subjectivity over time
- Sentiment comparison

### 4. Attachment
- Radar chart (anxious/avoidant/secure/controlling)
- Attachment markers over time
- Style interpretation

### 5. Patterns
- Love bombing scatter plot
- Spike/withdrawal counts
- Intermittent reinforcement count

### 6. Conflicts
- High-conflict days table
- Conflict severity badges
- Temporal conflict distribution

### 7. Dynamics
- Double-texting comparison
- Flooding comparison
- Response time bar chart
- Initiation ratio

### 8. Network
- D3.js force-directed graph
- Third-party table
- Relationship terms table

### 9. Findings
- Auto-generated findings
- Critical/warning/info badges

## CSS Theme (Dark)

```css
:root {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --border: #334155;
    --accent-blue: #3b82f6;
    --accent-green: #22c55e;
    --accent-red: #ef4444;
    --accent-yellow: #eab308;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-secondary);
}

.card {
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
}

section {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 30px;
    margin: 20px 0;
}
```

## Chart.js Configuration

### Color Palette
```javascript
const colors = {
    blue: '#3b82f6',
    green: '#22c55e',
    red: '#ef4444',
    yellow: '#eab308',
    purple: '#a855f7',
    pink: '#ec4899',
    cyan: '#06b6d4'
};
```

### Dark Theme Options
```javascript
const darkOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { labels: { color: '#e2e8f0' } }
    },
    scales: {
        x: {
            ticks: { color: '#94a3b8' },
            grid: { color: '#334155' }
        },
        y: {
            ticks: { color: '#94a3b8' },
            grid: { color: '#334155' }
        }
    }
};
```

### Chart Types Used

| Chart | Type | Purpose |
|-------|------|---------|
| Monthly volume | Line (filled) | Message trends |
| Hourly dist | Bar (grouped) | Time patterns |
| Love:Negative | Line | Ratio tracking |
| Love/Negative | Bar (stacked) | Comparison |
| Sentiment | Line | Polarity trends |
| Attachment | Radar | Style profiles |
| Patterns | Scatter | Spike/withdrawal |
| Dynamics | Bar | Comparison |

## D3.js Network Graph

```javascript
const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2));

// Node sizing by importance
node.attr('r', d => d.group === 'main' ? 25 : 8 + d.mentions / 10);

// Link thickness by connection strength
link.attr('stroke-width', d => Math.min(d.value / 20, 3));
```

## Data Injection

```javascript
// In generate_report.py
html += f'''
<script>
    const DATA = {json.dumps(data, default=str)};
</script>
'''
```

### Data Structure
```javascript
DATA = {
    stats: {
        total_messages: number,
        total_words: number,
        date_range: { start: string, end: string },
        by_sender: { [name]: { messages: number, words: number } }
    },
    monthly: {
        'YYYY-MM': {
            [sender]: {
                messages: number,
                words: number,
                love: number,
                negative: number,
                sentiment: number
            }
        }
    },
    daily: { 'YYYY-MM-DD': { [sender]: number } },
    hourly: { [0-23]: { [sender]: number } },
    analysis: {
        sentiment: { ... },
        attachment: { [sender]: { anxious, avoidant, secure, controlling } },
        love_patterns: { spikes: [], withdrawals: [], intermittent_reinforcement_count },
        conflicts: { high_conflict_days: [], total_conflict_days },
        third_parties: { third_parties: [], relationship_terms: {} },
        dynamics: { double_texts, triple_floods, response_times, conversation_initiations }
    },
    attachment_monthly: { 'YYYY-MM': { [sender]: { anxious, avoidant, secure, controlling } } }
}
```

## Badge Classes

```html
<span class="badge badge-blue">Info</span>
<span class="badge badge-green">Good</span>
<span class="badge badge-yellow">Warning</span>
<span class="badge badge-red">Critical</span>
```

```css
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-blue { background: #1e40af; color: #93c5fd; }
.badge-green { background: #166534; color: #86efac; }
.badge-yellow { background: #854d0e; color: #fde047; }
.badge-red { background: #991b1b; color: #fca5a5; }
```

## Finding Cards

```html
<div class="finding critical">
    <h4>Title</h4>
    <p>Description</p>
</div>
```

```css
.finding {
    background: #0f172a;
    border-left: 4px solid #3b82f6;
    padding: 15px 20px;
    margin: 10px 0;
    border-radius: 0 8px 8px 0;
}
.finding.critical { border-left-color: #ef4444; }
.finding.warning { border-left-color: #f59e0b; }
```

## Auto-Generated Findings Logic

```javascript
// Communication asymmetry
if (senderPct > 55) {
    findings.push({
        type: 'warning',
        title: 'Communication Asymmetry',
        text: `${sender} sent ${pct}% of messages`
    });
}

// Love bombing
if (spikes.length > 50) {
    findings.push({
        type: 'critical',
        title: 'Love Bombing Detected',
        text: `${spikes.length} affection spikes detected`
    });
}

// Intermittent reinforcement
if (ir_count > 30) {
    findings.push({
        type: 'critical',
        title: 'Intermittent Reinforcement',
        text: `${ir_count} spike-withdrawal cycles`
    });
}
```
