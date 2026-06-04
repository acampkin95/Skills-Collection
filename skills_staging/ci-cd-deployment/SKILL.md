---
name: ci-cd-deployment
description: CI/CD pipelines and deployment — GitHub Actions, Docker Compose, and SFTP/rsync to Tailscale hosts.
version: 2.0.0
reviewed: "2026-06-04"
---

# CI/CD & Deployment — Master Router

## Router

| Need | Route to |
| --- | --- |
| GitHub Actions workflow YAML, matrix builds, reusable actions | `github-actions-ci` |
| Docker Compose multi-container stacks (local or prod) | `docker-compose` |
| SFTP/rsync deployment over Tailscale | `sftp` |
