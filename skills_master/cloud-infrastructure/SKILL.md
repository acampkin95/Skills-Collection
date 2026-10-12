---
name: cloud-infrastructure
description: Routes cloud infrastructure requests for Cloudflare DNS and Workers, Tailscale, S3-compatible object storage, GitHub automation, and OVHcloud dedicated servers to the right skill. Use when managing DNS records, Cloudflare Workers, Tailscale hosts, S3 buckets, or OVHcloud dedicated server lifecycle, IPMI, or firewall settings.
version: 2.0.0
reviewed: "2026-10-12"
---

# Cloud Infrastructure — Master Router

## Router

| Need | Route to |
| --- | --- |
| Cloudflare DNS/Workers, Tailscale, S3 storage, GitHub automation | `cloud-api-management-cli` |
| OVHcloud dedicated server API (lifecycle, IPMI/KVM, firewall, bandwidth) | `ovhcloud-dedicated` |
