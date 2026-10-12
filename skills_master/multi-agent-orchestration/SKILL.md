---
name: multi-agent-orchestration
description: "Multi-agent orchestration router: sends Claude Code CLI and MCP setup, autonomous agent project management, multi-agent task planning, CrewAI crews and flows, and agent prompt patterns to the matching sub-skill. Use when setting up a multi-agent workflow, decomposing a task for parallel agents, configuring a coding agent CLI or MCP server, or building a CrewAI crew."
version: 2.0.0
reviewed: "2026-10-12"
---

# Multi-Agent Orchestration — Master Router

Route to the narrowest leaf that matches the framework or workflow you need.

## Router

| Need | Route to |
| --- | --- |
| Claude Code CLI, MCP server setup, OMC mode | `configuring-coding-agent-cli` (sub-skill folder in this skill) |
| Autonomous agent orchestration, burndown charts, checkpointing | `ai-project-management` |
| Decompose complex tasks, parallel agents, dependency graph | `multi-agent-planner` |
| CrewAI multi-agent framework (crews, tasks, flows) | `crewai-setup` |
| Prompt engineering patterns for agents (CoT, ReAct, structured output) | `prompt-engineering` |

## See also

- [nextjs](../nextjs/SKILL.md) — Next.js framework (uses these patterns heavily)
- [code-quality](../code-quality/SKILL.md) — quality gates for agent code
