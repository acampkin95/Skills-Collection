---
name: ci-cd-deployment
description: Routes CI/CD and deployment requests to the right skill for GitHub Actions workflows, Docker Compose stacks, and SFTP or rsync deployment to Tailscale hosts. Use when building or fixing a CI/CD pipeline, choosing a GitHub Actions, Docker Compose, or SFTP deployment path, or deploying an app to a server.
version: 2.0.0
reviewed: "2026-10-12"
---

# CI/CD & Deployment — Master Router

## Router

| Need | Route to |
| --- | --- |
| GitHub Actions workflow YAML, matrix builds, reusable actions | `github-actions-ci` |
| Docker Compose multi-container stacks (local or prod) | `docker-compose-cli` |
| SFTP/rsync deployment over Tailscale | `sftp-cli` |
