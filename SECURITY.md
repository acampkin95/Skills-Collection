# Security Policy

## Why this matters here specifically

Skills in this repository are instructions an AI agent follows, often with
tool access — several (`ssh-infrastructure`, `proxmox-admin`,
`ovhcloud-dedicated`, `open-webui-admin`, `cloud-api-management`,
`acdev-deployment`) describe how to reach real servers, cloud APIs, and
infrastructure. Treat every skill as potentially executable policy, not
just documentation.

## Reporting a vulnerability

If you find a security issue in this repository — a committed credential,
a skill that would guide an agent into an unsafe or destructive action
without confirmation, or a supply-chain issue in a script or dependency —
open a private security advisory on GitHub (Security tab → "Report a
vulnerability") rather than a public issue.

## Never commit

- Real API keys, tokens, SSH keys, or certificates — including in example
  code. Use obvious placeholders (`sk-xxxxxxxxxxxxxxxxxxxx`,
  `<your-api-key>`), never a redacted-but-real-shaped value.
- Real hostnames, IP addresses, Tailscale/WireGuard configuration, or
  Proxmox/OVH API tokens belonging to actual infrastructure.
- Docker socket paths or credentials that would grant host-level access.
- Real log excerpts, packet captures, or diagnostic output — these commonly
  carry secrets or personal data even when the person sharing them doesn't
  notice.
- Personal data (names, addresses, case details) in examples for the legal
  or CSV-forensics skills — use synthetic fixtures instead.

CI runs a frontmatter/metadata check
(`SkillsFramework/scripts/validate_skills.py`) and a gitleaks secret scan
on every pull request, but neither is a substitute for reviewing your own
diff before pushing.

## Skill safety metadata

High-impact skills should declare this in their `SKILL.md` frontmatter
(see [`schema/skill.schema.json`](schema/skill.schema.json)):

```yaml
risk: high
requires_confirmation: true
permissions:
  filesystem: write
  shell: restricted
  network: restricted
  secrets: true
```

This doesn't enforce anything at runtime — it documents, for anyone
reviewing or converting the skill, that it should not run destructive,
external, or credential-using actions without the operator confirming
first.

## Scope

This policy covers the repository's own content and tooling
(`SkillsFramework/`, packaging/conversion scripts, skill content). It does
not cover the security of infrastructure that a skill merely documents how
to administer (e.g. a bug in Proxmox itself) — report those upstream.
