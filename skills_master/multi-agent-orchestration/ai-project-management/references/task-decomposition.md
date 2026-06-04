# Task Decomposition Strategies

This document outlines strategies for breaking down complex development tasks into manageable subtasks suitable for AI agent execution.

## Overview

Effective task decomposition is critical for:
- Enabling parallel execution
- Managing agent workload
- Tracking progress accurately
- Handling failures gracefully

## Decomposition Approaches

### 1. Functional Decomposition

**Description:** Break down tasks by function or feature component. Each subtask addresses a specific functional area.

**Approach:**
- Identify major functional components
- Map dependencies between components
- Create subtasks for each component
- Order by dependency flow

**Example:**
```
Task: Build E-commerce Platform

Subtasks:
├── User Management
│   ├── Authentication
│   ├── Profile management
│   └── Authorization
├── Product Catalog
│   ├── Product listing
│   ├── Search
│   └── Product details
├── Shopping Cart
│   ├── Add/remove items
│   ├── Update quantities
│   └── Cart persistence
├── Checkout
│   ├── Address collection
│   ├── Payment processing
│   └── Order confirmation
└── Notifications
    ├── Email
    └── SMS
```

**Implementation:**
```python
from scripts.task_decomposer import TaskDecomposer

decomposer = TaskDecomposer()

result = decomposer.decompose(
    task_description="Build an e-commerce platform with user management, "
                    "product catalog, shopping cart, and checkout functionality",
    context={"project_type": "web_application"}
)
```

**When to Use:**
- Feature-rich applications
- Clear component boundaries
- When parallelization is desired

### 2. Layer Decomposition

**Description:** Break down tasks by system layer (presentation, business logic, data access).

**Approach:**
- Identify system layers
- Create subtasks per layer
- Order bottom-up (data first)
- Include integration tasks

**Example:**
```
Task: Implement User Authentication

Layers:
├── Data Layer
│   ├── User model
│   ├── Database schema
│   └── Repository
├── Service Layer
│   ├── Auth service
│   ├── Token service
│   └── User service
├── API Layer
│   ├── Login endpoint
│   ├── Register endpoint
│   └── Profile endpoint
└── Frontend
    ├── Login form
    ├── Register form
    └── Session management
```

**When to Use:**
- Layered architectures
- When clean separation is important
- Multi-tier applications

### 3. Feature-Based Decomposition

**Description:** Break down by user-facing features with end-to-end implementation.

**Approach:**
- Identify user features
- Create feature squads
- Each subtask delivers complete feature
- Include testing and docs

**Example:**
```
Task: Feature: Social Sharing

Subtasks:
├── Feature: Share button component
│   ├── UI implementation
│   ├── API integration
│   └── Unit tests
├── Feature: Share dialog
│   ├── Modal design
│   ├── Platform selection
│   └── Preview functionality
├── Feature: Analytics tracking
│   ├── Event tracking
│   ├── Dashboard update
│   └── Report generation
└── Feature: Admin controls
    ├── Configuration UI
    ├── Rate limiting
    └── Audit logging
```

**When to Use:**
- Agile methodologies
- User story mapping
- Sprint planning

### 4. Risk-Based Decomposition

**Description:** Prioritize high-risk areas first, decompose to isolate risk.

**Approach:**
- Identify technical risks
- Address complex items early
- Create spike tasks for unknowns
- Defer stable areas

**Example:**
```
Task: Legacy System Migration

By Risk:
├── HIGH RISK (Address First)
│   ├── Data migration strategy
│   ├── API compatibility layer
│   └── Authentication migration
├── MEDIUM RISK
│   ├── Core business logic
│   ├── Reporting features
│   └── Notification system
└── LOW RISK (Can Wait)
    ├── UI improvements
    ├── Performance tuning
    └── Documentation
```

**When to Use:**
- High-risk projects
- Unknown technical territory
- When early risk identification is critical

## Decomposition Principles

### 1. Task Size Guidelines

| Size Category | Duration | Description |
|--------------|----------|-------------|
| Small | 5-15 min | Single file, simple change |
| Medium | 15-60 min | One feature, multiple files |
| Large | 1-4 hours | Complex feature, testing |
| Epic | 4+ hours | Break down further |

### 2. Subtask Characteristics

Good subtasks should be:

- **Independent:** Can be completed without other subtasks
- **Estimable:** Can estimate effort accurately
- **Valuable:** Delivers tangible value
- **Small Enough:** Fits in single work session
- **Testable:** Has clear completion criteria

### 3. Dependency Management

```python
# From task_decomposer.py
subtask_1 = Subtask(
    id="st-1",
    name="Database schema design",
    dependencies=[],  # No dependencies
    parallelizable=False
)

subtask_2 = Subtask(
    id="st-2",
    name="API endpoints implementation",
    dependencies=["st-1"],  # Depends on schema
    parallelizable=True
)

subtask_3 = Subtask(
    id="st-3",
    name="Frontend integration",
    dependencies=["st-2"],  # Depends on API
    parallelizable=False
)
```

### 4. Effort Estimation

The decomposer uses multiple factors:

```python
# Estimation factors
estimation_factors = {
    "complexity": 1.0,           # Base multiplier
    "task_type": {               # Type adjustments
        "feature": 1.2,
        "bug_fix": 0.8,
        "refactor": 1.5,
        "documentation": 0.6
    },
    "uncertainty": 1.0,          # Risk adjustment
    "team_familiarity": 1.0      # Experience factor
}
```

## Automatic Decomposition

The `TaskDecomposer` class provides automated decomposition:

```python
from scripts.task_decomposer import TaskDecomposer, TaskPriority

decomposer = TaskDecomposer({
    "use_templates": True,
    "default_subtask_size": "medium"
})

# Decompose a task
result = decomposer.decompose(
    task_description="Implement user authentication with OAuth2",
    task_id="auth-feature",
    context={"framework": "fastapi"}
)

# Access results
for subtask in result.subtasks:
    print(f"{subtask.name}: {subtask.estimated_minutes} min")
    print(f"  Capabilities: {subtask.required_capabilities}")
    print(f"  Dependencies: {subtask.dependencies}")

# Get parallel groups
print(f"Parallel execution groups: {result.parallel_groups}")

# Get critical path
print(f"Critical path: {result.critical_path}")
```

## Manual Decomposition

For full control, create subtasks manually:

```python
from scripts.task_decomposer import Subtask, TaskType, TaskComplexity

subtasks = [
    Subtask(
        id="st-1",
        name="Design authentication flow",
        description="Create architecture for OAuth2 authentication",
        task_type=TaskType.FEATURE_IMPLEMENTATION,
        complexity=TaskComplexity.MODERATE,
        estimated_minutes=60,
        required_capabilities=["design", "security"],
        acceptance_criteria=[
            "Flow diagram created",
            "Security review completed"
        ],
        parallelizable=False
    ),
    Subtask(
        id="st-2",
        name="Implement OAuth2 provider",
        description="Code OAuth2 provider integration",
        task_type=TaskType.FEATURE_IMPLEMENTATION,
        complexity=TaskComplexity.COMPLEX,
        estimated_minutes=180,
        required_capabilities=["python", "oauth"],
        dependencies=["st-1"]
    )
]
```

## Quality Checks

After decomposition, validate:

```python
result = decomposer.decompose(task)

# Validation checks
validations = {
    "has_subtasks": len(result.subtasks) > 0,
    "has_parallel_groups": len(result.parallel_groups) > 1,
    "critical_path_defined": len(result.critical_path) > 0,
    "reasonable_estimates": all(
        s.estimated_minutes < 240 for s in result.subtasks
    ),
    "no_circular_deps": decomposer._check_circular_dependencies(result.subtasks)
}

for check, passed in validations.items():
    status = "PASS" if passed else "FAIL"
    print(f"{check}: {status}")
```

## Best Practices

1. **Start High-Level:** Begin with major components
2. **Iterate Refinement:** Break down iteratively
3. **Consider Context:** Account for project specifics
4. **Plan for Chaos:** Include buffer tasks
5. **Review Regularly:** Validate decomposition quality

## Common Pitfalls

| Pitfall | Symptoms | Solution |
|---------|----------|----------|
| Too granular | Many tiny tasks, overhead | Aim for 15-60 min tasks |
| Too coarse | Large ambiguous tasks | Break down until clear |
| Missing dependencies | Tasks blocked unexpectedly | Map all dependencies |
| Ignoring risk | Unplanned delays | Risk-based prioritization |

## See Also

- [Agent Patterns](agent-patterns.md)
- [Workflow Orchestration](../scripts/workflow-orchestrator.py)
- [Metrics and KPIs](metrics-kpis.md)
