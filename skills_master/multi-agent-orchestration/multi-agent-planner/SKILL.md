---

## Parent router

This skill is a leaf of the [multi-agent-orchestration](../multi-agent-orchestration/SKILL.md) master router.
name: multi-agent-planner
description: Multi-agent planning, agent orchestration, task decomposition, parallel agents, complex workflows, Perplexity research. Use when planning architect, research specialist, data analyst, DAG of subtasks, parallel agent execution.
---

# Multi-Agent Planner

Coordinate complex tasks by spawning and orchestrating specialized sub-agents.

## When to use

- Tasks with 3+ independent work streams that can run in parallel
- Projects requiring live research + analysis + planning
- Workflows where one agent's output feeds another's input

## Core roles

- **Planning Architect** — produces roadmaps, milestones, dependency graphs
- **Research Specialist** — gathers live data via Perplexity / web search
- **Data Analyst** — interprets quantitative constraints, metrics, cost/latency budgets

## Workflow

1. **Decompose** the request into a DAG of subtasks (dependencies explicit).
2. **Assign** each node to a role; mark nodes that can run in parallel.
3. **Spawn** agents with bounded context windows; collect outputs.
4. **Reconcile** conflicting outputs; surface trade-offs to the user.
5. **Synthesize** into a single actionable plan with owners and deadlines.

## Best practices

- Keep each agent's prompt narrow (one role, one task, one output format).
- Pass structured handoffs (JSON / Markdown tables), not free-form prose.
- Set a max-iteration cap to prevent loops.
- Always include a final human-readable summary.

## See also

- [claude-code](../claude-code/SKILL.md) — Claude Code CLI + MCP orchestration (overlapping domain)
- [ai-project-management](../ai-project-management/SKILL.md) — burndown charts, checkpointing
- [crewai-setup](../crewai-setup/SKILL.md) — CrewAI-specific multi-agent framework
