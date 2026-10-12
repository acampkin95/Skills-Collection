---
name: code-quality
description: Routes code quality requests to Biome linting, SonarScanner analysis, quality-control gates, or code audits for JavaScript, TypeScript, and Python projects. Use when setting up linting or formatting, running SonarScanner or a quality gate, auditing code for security issues, or combining these checks into one pipeline.
version: 2.0.0
reviewed: "2026-10-12"
---

# Code Quality — Master Router

Route to the narrowest leaf that matches the tool or workflow you need.

## Router

| Need | Route to |
| --- | --- |
| Biome v2 linter/formatter (JS/TS) | `biome-linting-cli` |
| SonarScanner CLI for code quality + security | `sonar-scanner-cli` |
| General QA workflow / quality gate | `quality-control` |
| Security audit, vulnerability scan, code review | `code-audit` |

All four leaves can be combined in a single quality pipeline.
