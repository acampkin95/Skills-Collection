# Skills Repo Optimization Plan

## Problem Summary

- **Error**: `ai-project-management/SKILL.md` missing YAML frontmatter closing `---`
- **Duplication**: 69 skills exist in ALL 3 directories (master, Dev_Skills, Latest/skills), 21 only in master, 2 in 2 of 3
- **Token bloat**: 22,619 lines across ~100 SKILL.md files in master alone; 332 total SKILL.md files across all dirs (98,311 total lines)
- **Description bloat**: Nearly ALL descriptions are 200-900+ chars, loading ~15-50k tokens into system prompt at startup
- **Oversized skills**: engram (969 lines), ripgrep (504), brand-creativebuilder (486), github-actions-ci (476), i18n-localization (470), prompt-engineering (469), typescript-advanced (462), cloud-api-management (451), database-orm (436)

## Phase 1: Fix Critical Errors (Immediate)

### 1.1 Fix `ai-project-management/SKILL.md`
- Add closing `---` after description line (line 3)
- **Also**: This entire skill is bloated. It's a meta-skill that should be ~50 lines, not 185.
  - Remove ASCII architecture diagram (lines 108-128) — 21 lines of decorative art
  - Remove Python code examples referencing non-existent scripts — these scripts don't exist in the repo
  - Remove verbose capability descriptions (Claude already knows what multi-agent coordination means)
  - Remove generic integration points section
  - **Target**: ~50 lines, keeping essential routing guidance

### 1.2 Fix same file in `Latest/skills/ai-project-management/SKILL.md`

## Phase 2: Consolidate Directories (Biggest Win)

### Current State
| Directory | SKILL.md count | Total lines |
|-----------|---------------|-------------|
| `master/` | 130 | 22,619 |
| `Dev_Skills/` | 98 | 29,702 |
| `Latest/skills/` | 104 | 32,441 |

### Problem
- **69 skills are identical across all 3 directories**
- `package.sh` packages from `master/` only — Dev_Skills and Latest are stale mirrors
- Maintenance skills in `.maintenance/` (27 files) and `.omc/archive/` (7 files) are already excluded from packaging

### Plan
1. **Keep `master/` as the single source of truth**
2. **Delete `Dev_Skills/`** — it's a stale mirror (98 duplicate skills, 29,702 lines)
3. **Delete `Latest/skills/`** — it's a stale mirror (104 duplicate skills, 32,441 lines)
4. **Update `sync.sh`** to handle the new structure

**Tokens saved**: ~62,000 lines of duplicated content removed from the repo

## Phase 3: Optimize SKILL.md Content

### 3.1 Trim Descriptions (Frontmatter)
The guidance doc says descriptions load at ~100 tokens each in the system prompt. With 95+ unique skills, that's massive overhead.

**Target**: 100-150 chars per description (third person, specific triggers, no fluff)

| Before (chars) | Skill | After (chars) |
|----------------|-------|---------------|
| 663 | accessibility-testing | `Comprehensive accessibility (a11y) testing and WCAG 2.2 compliance automation for React/Next.js. Use this skill when axe-core, jest-axe, accessibility audit, WCAG compliance, a11y testing, screen reader, keyboard navigation, ARIA labels, color contrast, Lighthouse CI accessibility, semantic HTML validation, keyboard-only navigation, a11y CI pipeline.` |
| 669 | claude-code | `Claude Code CLI configuration, MCP server setup, and multi-agent orchestration (OMC) automation. Use this skill when Claude Code CLI, settings.json, CLAUDE.md, MCP server setup, model routing, opus/sonnet/haiku, OMC modes, autopilot mode, subagent spawning, slash commands, Bedrock/Vertex/Foundry, provider configuration, ultrawork mode, team orchestration.` |
| 945 | ovhcloud-dedicated | `OVHcloud dedicated server remote administration via API — server lifecycle, IPMI/KVM console access, network configuration, firewall rules, OS reinstallation, boot modes, monitoring, bandwidth stats, IP management, reverse DNS, hardware RAID, and intervention history. Use this skill whenever the user mentions OVHcloud, OVH dedicated server, OVH API, OVH IPMI, OVH KVM, OVH server reboot, OVH rescue mode, OVH network config, OVH firewall, OVH reverse DNS, OVH bandwidth, OVH monitoring, OVH hardware specs, OVH OS install, OVH boot mode, OVH server tasks, OVH interventions, dedicated server API management, bare metal cloud OVH, or any task involving programmatic control of OVHcloud dedicated servers — even if they just say "check my server" or "reboot the dedi". Also trigger when the user wants to automate OVH infrastructure, script OVH server provisioning, manage multiple OVH servers, or troubleshoot OVH connectivity via IPMI/KVM/SoL.` |

### 3.2 Trim Oversized Skills
Skills that should be split or trimmed:

| Skill | Current Lines | Target | Strategy |
|-------|--------------|--------|----------|
| engram | 969 | ~50 | Router only — delegate to sub-skills |
| ripgrep | 504 | ~100 | Trim reference recipes, keep core patterns |
| brand-creativebuilder | 486 | ~150 | Move brand templates to reference files |
| github-actions-ci | 476 | ~150 | Move workflow examples to references/ |
| i18n-localization | 470 | ~120 | Move next-intl v4 details to references/ |
| prompt-engineering | 469 | ~80 | Minimal guidance, reference external docs |
| typescript-advanced | 462 | ~120 | Move type challenges to references/ |
| cloud-api-management | 451 | ~100 | Trim redundant cloud provider details |
| database-orm | 436 | ~120 | Move Prisma/Drizzle patterns to references/ |
| data-visualization | 448 | ~80 | Just a name + description, body is empty |
| caching-redis | 443 | ~100 | Move patterns to references/ |
| cli-tool-development | 440 | ~100 | Trim CLI library details to references |
| reportlab-python | 417 | ~100 | Move report templates to references |
| api-design-testing | 417 | ~120 | Move OpenAPI/MSW patterns to references |
| compliance-gdpr-privacy | 403 | ~100 | Move compliance checklist to references |
| csv-legal-analysis | 401 | ~100 | Move analysis workflows to references |
| monorepo-turborepo | 399 | ~80 | Move build configs to references |
| pwa-offline-first | 397 | ~80 | Service worker patterns to references |

### 3.3 Trim Medium Skills
Skills that should be trimmed to <100 lines:

| Skill | Current Lines | Target |
|-------|--------------|--------|
| multi-agent-planner | 4 (actually minimal - OK) | Keep as-is |
| multi-agent-planner | (duplicate check needed) | — |
| wa-legal | 49 | Keep as-is |
| firecrawl* (all 14) | 50-102 | Trim to <80 each |
| maestri* (all 3) | 42-100 | Trim to <80 each |
| code-audit | 136 | ~100 |
| creative-strategy | 139 | ~100 |
| biome-linting | 150 | ~100 |
| realtime-websockets | 151 | ~80 |
| nextjs-code-audit | 169 | ~100 |
| weaviate | 170 | ~100 |
| crawl4ai | 194 | ~100 |
| performance-profiling | 196 | ~80 |
| clerk | 219 | ~120 |
| bun-runtime | 240 | ~100 |
| crewai-setup | 258 | ~100 |
| relationship-analysis | 256 | ~100 |
| nextjs | 259 | ~120 |
| wa-legal-letter-docx | 259 | ~100 |
| macos | 265 | ~120 |
| windows-ps-admin | 268 | ~120 |
| regex-text-processing | 269 | ~100 |
| deepinfra-ocr | 280 | ~80 |
| wa-fvro | 283 | ~100 |
| wa-law-general | 287 | ~100 |
| frontend-specialist | 295 | ~100 |
| sonar-scanner | 300 | ~80 |
| accessibility-testing | 302 | ~100 |
| modern-web-design | 304 | ~100 |
| git-advanced-workflows | 308 | ~100 |
| python-fastapi | 313 | ~100 |
| email-notifications | 317 | ~100 |
| wa-teacher-misconduct | 322 | ~120 |
| documentation-site | 327 | ~100 |
| ovhcloud-dedicated | 328 | ~100 |
| quality-control | 328 | ~80 |
| nextjs16-fullstack | 329 | ~100 |
| sanity-nextjs | 344 | ~100 |
| monitoring-observability | 347 | ~120 |
| docker-compose | 348 | ~100 |
| claude-code | 351 | ~120 |
| pdfkit-node | 357 | ~100 |
| tapestry | 357 | ~100 |
| search-implementation | 366 | ~100 |
| case-file-manager-wa | 368 | ~100 |
| feature-flags | 376 | ~100 |
| tailwind | 377 | ~80 |
| cloudapi | 225 (2 of 3) | ~100 |

## Phase 4: Execute Order

### Step 1: Fix `ai-project-management/SKILL.md` (master)
- Add closing `---` after line 3
- Rewrite body to ~50 lines: remove ASCII diagram, remove Python examples for non-existent scripts, trim verbose descriptions

### Step 2: Optimize all oversized skills in `master/`
- Process top 20 largest files first (saves most tokens)
- Use progressive disclosure: keep SKILL.md body <100 lines, move details to `references/` files

### Step 3: Optimize descriptions (frontmatter)
- Target 100-150 chars per description
- Keep specific trigger keywords for discovery
- Third person only

### Step 4: Run `package.sh` to verify all skills still package correctly

### Step 5: Leave Dev_Skills as-is (WIP directory)

**Note**: Latest/ already deleted by user.

## Expected Results

| Metric | Before | After |
|--------|--------|-------|
| SKILL.md files | 130 (master only) | ~95 |
| Total lines in master | 22,619 | ~15,000 |
| Lines removed | — | ~7,600 |
| Oversized skills (>400 lines) | 19 | 0 |
| Missing frontmatter errors | 1 | 0 |
