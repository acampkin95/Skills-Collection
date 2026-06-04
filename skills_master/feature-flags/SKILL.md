---
name: feature-flags
description: Feature flag systems with LaunchDarkly, Statsig, and GrowthBook. Use for gradual rollouts, A/B testing, kill switches, and targeting rules.
version: 2.0.0
reviewed: "2026-06-04"
---
# Feature Flags

Feature flag management for controlled releases, A/B testing, and operational control.

## Flag Types

| Type | Purpose | Lifetime | Example |
|------|---------|----------|---------|
| **Release** | Gate incomplete features | Days–weeks | `new-checkout-flow` |
| **Experiment** | A/B test variants | Weeks–months | `pricing-page-v2` |
| **Ops** | Kill switch / circuit breaker | Permanent | `enable-search-cache` |
| **Permission** | User-level access control | Permanent | `beta-access` |

## 2025-2026 Platform Landscape

For teams at scale, consider managed platforms:

| Platform | Best For | Pricing | Key Features |
|----------|----------|---------|--------------|
| **LaunchDarkly** | Enterprise DevOps teams | $10+/mo | Enterprise security, advanced targeting, integrations |
| **Statsig** | Product teams + experimentation | Free-$150+/mo | Built-in statistical analysis, experimentation framework |
| **GrowthBook** | Open-source or growth teams | Free (open) | A/B testing focus, experimentation, cost-effective |
| **Flagsmith** | Small-to-medium teams | Free tier + paid | Lightweight, developer-friendly, event tracking |

**2025 Trend**: 96% of high-growth companies (expected 2025+ growth) invest in feature experimentation.

## References

- [Implementation patterns](references/implementation-patterns.md) — LaunchDarkly, Statsig, Edge Config integration (2025+)
- [Testing with flags](references/testing-with-flags.md) — test fixtures, flag combinations, stale flag cleanup


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.