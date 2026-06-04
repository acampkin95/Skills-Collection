---

## Parent router

This skill is a leaf of the [multi-agent-orchestration](../multi-agent-orchestration/SKILL.md) master router.
name: ai-project-management
description: Autonomous agent orchestration for AI-augmented development. Use when multi-agent coordination, task decomposition, checkpointing, burndown charts, workflow orchestration, autonomous coding sessions.
---

# AI Project Management Skill

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

### Starting a Multi-Agent Project

```python
from scripts.agent_coordinator import AgentCoordinator
from scripts.task_decomposer import TaskDecomposer
from scripts.checkpoint_manager import CheckpointManager

# Initialize components
coordinator = AgentCoordinator()
decomposer = TaskDecomposer()
checkpoint_manager = CheckpointManager()

# Decompose a complex task
task = "Build a full-stack e-commerce application"
subtasks = decomposer.decompose(task)

# Create agents for each major component
for subtask in subtasks:
    agent = coordinator.create_agent(
        name=subtask.name,
        capabilities=subtask.required_skills,
        priority=subtask.priority
    )

# Start coordinated work
coordinator.start_all_agents()
```

### Managing Development Sessions

```python
from scripts.session_manager import SessionManager
from scripts.progress_tracker import ProgressTracker

session_mgr = SessionManager()
progress = ProgressTracker()

# Create a new session
session_id = session_mgr.create_session(
    project_name="my-project",
    context={"goals": ["feature-a", "feature-b"]}
)

# Track progress
progress.update_milestone("feature-a", status="completed")
status = progress.get_project_status()
```

### Setting Up Quality Gates

```python
from scripts.quality_gate import QualityGate
from scripts.cost_estimator import CostEstimator

gate = CostEstimator()
gate.set_budget(max_tokens=1000000, max_cost=50.00)

# Run quality checks
results = gate.run_checks(
    min_test_coverage=80,
    require_security_scan=True,
    max_complexity=10
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
