# Project Metrics and KPIs

This document defines the key metrics and KPIs for tracking AI-assisted project performance and agent effectiveness.

## Overview

Effective measurement enables:
- Identifying bottlenecks
- Optimizing agent allocation
- Tracking project health
- Continuous improvement

## Metric Categories

### 1. Velocity Metrics

**Definition:** Measures the rate of value delivery over time.

**Key Metrics:**

| Metric | Formula | Target | Description |
|--------|---------|--------|-------------|
| Sprint Velocity | Sum of completed story points | 20-40 pts/sprint | Average points per sprint |
| Commitment Accuracy | Committed / Completed | > 85% | How often commitments are met |
| Velocity Trend | Current / Previous sprint | +5% to +15% | Trajectory of delivery |
| Cycle Time | Start to Complete (hours) | < 24 hrs | Time to complete tasks |

**Tracking Implementation:**
```python
from scripts.progress_tracker import ProgressTracker

tracker = ProgressTracker()

# Record completed task
tracker.log_progress(
    task_id="task-123",
    completed_items=5,
    remaining_items=0,
    contributed_by="agent-frontend"
)

# Get velocity metrics
velocity = tracker.get_velocity_metrics()
print(f"Average Velocity: {velocity['average_velocity']}")
print(f"Trend: {velocity['velocity_trend']}")
print(f"Sprint Capacity: {velocity['sprint_capacity']}")
```

### 2. Quality Metrics

**Definition:** Measures code quality and defect rates.

**Key Metrics:**

| Metric | Formula | Target | Description |
|--------|---------|--------|-------------|
| Test Coverage | Lines covered / Total lines | > 80% | Percentage of code tested |
| Bug Density | Bugs / KLOC | < 5 | Bugs per thousand lines |
| Code Review Coverage | Reviewed / Total PRs | 100% | Code review participation |
| Rework Rate | Reworked / Total completed | < 10% | Work that needs revision |

**Tracking Implementation:**
```python
from scripts.quality_gate import QualityGate

gate = QualityGate({
    "min_test_coverage": 80.0
})

results = gate.run_checks()

for result in results:
    print(f"{result.gate_type.value}: {result.status.value}")
    if result.metrics:
        print(f"  Metrics: {result.metrics}")
```

### 3. Agent Performance Metrics

**Definition:** Measures individual agent effectiveness.

**Key Metrics:**

| Metric | Formula | Target | Description |
|--------|---------|--------|-------------|
| Task Completion Rate | Completed / Assigned | > 90% | Agent task success rate |
| First-Pass Success | No revision needed / Completed | > 80% | Quality on first attempt |
| Average Task Duration | Total time / Tasks | < planned | Time vs estimate accuracy |
| Context Switching | Task changes / Time | Low | How often agents switch tasks |

**Agent Status Tracking:**
```python
from scripts.agent_coordinator import AgentCoordinator

coordinator = AgentCoordinator()

# Get agent statistics
status = coordinator.get_project_status()
print(f"Total agents: {status['agents']['total']}")
print(f"Working: {status['agents']['by_status']['working']}")
print(f"Idle: {status['agents']['by_status']['idle']}")

# Individual agent metrics
agent_status = coordinator.get_agent_status("agent-123")
print(f"Current task: {agent_status['current_task']}")
print(f"Uptime: {agent_status.get('uptime', 'N/A')}")
```

### 4. Cost Metrics

**Definition:** Measures resource efficiency and cost-effectiveness.

**Key Metrics:**

| Metric | Formula | Target | Description |
|--------|---------|--------|-------------|
| Cost per Feature | Total cost / Features | Decreasing | Cost efficiency |
| Token Efficiency | Value tokens / Total tokens | > 0.5 | Meaningful token usage |
| Budget Variance | Actual / Budget | < 100% | Spending vs plan |
| Model Selection | Cheaper model used | Maximize | Optimal model choice |

**Cost Tracking:**
```python
from scripts.cost_estimator import CostEstimator

estimator = CostEstimator()
estimator.set_budget(max_cost=100.0, max_tokens=500000)

# Log usage
estimator.log_usage(
    model_name="MiniMax-M2",
    input_tokens=5000,
    output_tokens=2000
)

# Get status
status = estimator.get_current_status()
print(f"Total cost: ${status['total_cost']}")
print(f"Budget remaining: ${status['budget']['budget_remaining']}")
```

### 5. Cycle Time Metrics

**Definition:** Measures time through different stages.

**Key Metrics:**

| Stage | Metric | Target | Description |
|-------|--------|--------|-------------|
| Planning | Planning time / Task | < 10% | Time to plan tasks |
| Development | Dev time / Task | Variable | Time in active development |
| Review | Review time / Task | < 4 hrs | Time in code review |
| Total | End-to-end time | Decreasing | Overall cycle time |

**Cycle Time Analysis:**
```python
from scripts.progress_tracker import ProgressTracker

tracker = ProgressTracker()

# Get cycle time metrics
cycle_time = tracker.get_cycle_time_metrics()
print(f"Average cycle time: {cycle_time['average_cycle_time']} hours")
print(f"P50: {cycle_time['p50']} hours")
print(f"P90: {cycle_time['p90']} hours")
```

## KPI Dashboard

**Combined Dashboard View:**
```python
def generate_kpi_dashboard():
    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "velocity": tracker.get_velocity_metrics(),
        "quality": gate.get_summary(),
        "cost": estimator.get_current_status(),
        "cycle_time": tracker.get_cycle_time_metrics()
    }

    # Calculate overall health score
    health_score = (
        min(dashboard['velocity'].get('velocity_trend', 0), 1) * 0.2 +
        (dashboard['quality']['passed'] / dashboard['quality']['total_checks']) * 0.3 +
        (1 - dashboard['cost'].get('budget', {}).get('budget_used_percent', 0) / 100) * 0.3 +
        (1 - min(dashboard['cycle_time'].get('p90', 24) / 24, 1)) * 0.2
    )

    dashboard['health_score'] = round(health_score * 100, 1)
    return dashboard
```

## Metric Collection Guidelines

### 1. Collection Frequency

| Metric Type | Frequency | Method |
|-------------|-----------|--------|
| Real-time | Continuous | Agent heartbeat |
| Hourly | Hourly | Cron job aggregation |
| Daily | Daily | Overnight batch |
| Sprint | Per sprint | Sprint retrospective |

### 2. Data Quality

```python
# Validation checks
def validate_metrics(metrics):
    validations = {
        "no_nulls": all(v is not None for v in metrics.values()),
        "positive_values": all(v >= 0 for v in metrics.values() if isinstance(v, (int, float))),
        "reasonable_ranges": all(0 <= v <= 100 for v in metrics.get('percentages', {}).values()),
        "consistent_schema": validate_schema(metrics)
    }
    return validations
```

### 3. Reporting Cadence

- **Daily:** Brief team sync on blockers
- **Weekly:** Velocity and progress review
- **Sprint End:** Full retrospective with all metrics
- **Monthly:** Trend analysis and capacity planning

## Target Setting

**SMART Targets:**

| Category | Current | Target | Timeline |
|----------|---------|--------|----------|
| Velocity | 25 pts | 30 pts | 2 sprints |
| Coverage | 75% | 85% | 1 sprint |
| Cycle Time | 24 hrs | 16 hrs | 3 sprints |
| Cost/Feature | $50 | $40 | 1 month |

## Best Practices

1. **Measure What Matters:** Focus on outcome metrics, not activity
2. **Automate Collection:** Reduce manual data entry
3. **Review Regularly:** Use metrics in retrospectives
4. **Iterate Targets:** Adjust based on historical data
5. **Avoid Gaming:** Metrics should measure true value

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Vanity metrics | Looks good, no meaning | Focus on leading indicators |
| Too many metrics | Analysis paralysis | Limit to 5-7 key metrics |
| Lagging only | Reactive, not proactive | Include leading indicators |
| No baselines | No improvement context | Establish baseline first |

## See Also

- [Progress Tracking](../scripts/progress-tracker.py)
- [Quality Gates](../scripts/quality-gate.py)
- [Cost Estimation](../scripts/cost-estimator.py)
