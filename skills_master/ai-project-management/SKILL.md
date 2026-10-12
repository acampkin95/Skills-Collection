---
name: ai-project-management
description: Coordinates multi-agent AI software projects with task decomposition, checkpointing, session management, progress tracking, YAML workflow definitions, quality gates, and cost estimation. Use when splitting a large feature into agent subtasks, coordinating autonomous coding agents, saving and resuming long-running agent work, tracking milestones or burndown, or estimating AI project token costs.
version: "1.0.0"
---

## Overview

This skill provides comprehensive capabilities for managing AI-driven development projects, orchestrating autonomous agents, and implementing robust project management workflows for AI-augmented software development.

## Core Capabilities

### Multi-Agent Coordination
- **Agent Lifecycle Management**: Create, monitor, and terminate AI agents dynamically
- **Task Distribution**: Intelligent task allocation based on agent capabilities and workload
- **Communication Framework**: Message passing and event coordination between agents
- **Resource Tracking**: Monitor and optimize resource utilization across agents

### Project Management
- **Task Decomposition**: Automatically break down complex tasks into manageable subtasks
- **Progress Tracking**: Real-time project status with burndown charts and velocity metrics
- **Checkpoint Management**: Save and restore agent state for long-running operations
- **Session Management**: Preserve context and resume development sessions

### Workflow Orchestration
- **Workflow Definitions**: YAML/JSON-based workflow specifications
- **Dependency Management**: Handle task dependencies and execution order
- **Error Recovery**: Automatic retry and fallback mechanisms
- **Visualization**: Workflow diagrams and progress dashboards

### Quality Assurance
- **Automated Quality Gates**: Enforce code quality standards automatically
- **Cost Estimation**: Track and optimize AI project costs
- **Security Scanning**: Integrate security checks into workflows
- **Performance Benchmarks**: Measure and track performance metrics

## Usage Examples

The bundled scripts use hyphenated filenames (for example `scripts/agent-coordinator.py`), which Python cannot import directly. Load them with `importlib.util` or copy them to underscore module names (`agent_coordinator.py`) before importing. Each script also has a CLI entry point (`python3 scripts/<name>.py --help`).

### Starting a Multi-Agent Project

```python
from agent_coordinator import AgentCoordinator
from task_decomposer import TaskDecomposer
from checkpoint_manager import CheckpointManager

coordinator = AgentCoordinator()
decomposer = TaskDecomposer()
checkpoints = CheckpointManager()

# Decompose a complex task into subtasks with dependencies
result = decomposer.decompose("Build a full-stack e-commerce application")

# Create one agent per subtask
for subtask in result.subtasks:
    coordinator.create_agent(
        name=subtask.name,
        capabilities=subtask.required_capabilities,
    )

# Save a checkpoint at a natural pause point
checkpoints.create_checkpoint(
    name="decomposition-complete",
    checkpoint_type="task",
    state={"task_id": result.task_id, "subtask_count": len(result.subtasks)},
)
```

### Managing Development Sessions

```python
from session_manager import SessionManager
from progress_tracker import ProgressTracker, MilestoneStatus

sessions = SessionManager()
progress = ProgressTracker()

session = sessions.create_session(
    name="feature-a-sprint",
    project="my-project",
    goals=["feature-a", "feature-b"],
)

milestone = progress.create_milestone(name="feature-a", description="Feature A ready for review")
progress.update_milestone(milestone.id, status=MilestoneStatus.COMPLETED)
status = progress.get_project_status()
```

### Setting Up Quality Gates

```python
from cost_estimator import CostEstimator
from quality_gate import QualityGate, GateType

estimator = CostEstimator()
estimator.set_budget(max_tokens=1_000_000, max_cost=50.00)

gate = QualityGate()
results = gate.run_checks(
    gate_types=[GateType.TEST_COVERAGE, GateType.SECURITY, GateType.COMPLEXITY],
)
```

## Architecture

### Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Project Management                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Session    │  │    Task      │  │   Agent Coordinator  │  │
│  │   Manager    │  │  Decomposer  │  │                      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         └─────────────────┼──────────────────────┘              │
│                           │                                     │
│  ┌────────────────────────┼───────────────────────────────┐     │
│  │                   Workflow Orchestrator                │     │
│  └────────────────────────┬───────────────────────────────┘     │
│                           │                                     │
│  ┌──────────────┐  ┌──────┴───────┐  ┌──────────────────────┐  │
│  │   Checkpoint │  │   Progress   │  │     Quality Gate     │  │
│  │   Manager    │  │   Tracker    │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Patterns

1. **Supervisor-Worker**: Hierarchical control with a supervisor agent delegating to workers
2. **Peer-to-Peer**: Equal agents collaborating on shared goals
3. **Hierarchical**: Multiple levels of management for complex projects
4. **Federated**: Distributed agents with centralized coordination

## Best Practices

### Checkpoint Strategy
- Create checkpoints at natural pause points
- Include full context: task state, code changes, decisions made
- Use descriptive checkpoint names for easy identification
- Regular checkpoints for long-running operations

### Task Decomposition
- Aim for subtasks that complete in 5-15 minutes
- Identify dependencies early to enable parallelization
- Estimate effort to balance workload across agents
- Leave room for emergent tasks

### Quality Gates
- Run automated checks before human review
- Enforce minimum test coverage thresholds
- Include security scanning in CI pipeline
- Track metrics over time for trends

## Integration Points

### Claude Code CLI
- Use subagent delegation for parallel work
- Implement session logging for audit trails
- Leverage checkpointing for complex refactors

### CI/CD Systems
- Trigger workflows from git events
- Report status to external systems
- Integrate with existing testing pipelines

### Monitoring
- Export metrics to Prometheus/Grafana
- Send alerts on quality gate failures
- Track agent performance over time

## References

- `references/agent-patterns.md` - Multi-agent collaboration patterns
- `references/task-decomposition.md` - Task breakdown strategies
- `references/checkpointing.md` - State management best practices
- `references/metrics-kpis.md` - Project metrics and KPIs
- `references/deployment-pipeline.md` - CI/CD for AI projects
- `references/autonomous-coding.md` - Autonomous coding guidelines

## Examples

See `examples/example-workflow.yaml` for a complete workflow definition example.
