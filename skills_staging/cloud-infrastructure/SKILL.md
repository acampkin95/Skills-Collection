---
name: cloud-infrastructure
description: Cloud infrastructure, — Cloudflare, Tailscale, S3, OVHcloud dedicated servers.
version: 2.0.0
reviewed: "2026-06-04"
---

# Cloud Infrastructure — Master Router

## Router

| Need | Route to |
| --- | --- |
| Cloudflare DNS/Workers, Tailscale, S3 storage, GitHub automation | `cloud-api-management` |
| OVHcloud dedicated server API (lifecycle, IPMI/KVM, firewall, bandwidth) | `ovhcloud-dedicated` |
