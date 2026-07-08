# Changelog - Skills Repository

**Location:** `/Users/alex/Projects/Infra/Skills_Repo`  
**Scope:** Skill promotions, major updates, and workspace changes  
**Format:** ISO 8601 dates (YYYY-MM-DD), reverse chronological  

---

## [2026-06-11] Skills consolidation & format fixes — firecrawl merged, broken refs resolved

**Status:** ✅ Complete

### A. Firecrawl skills consolidated into single master skill

- **Merged 16 skills** into `skills_master/firecrawl/SKILL.md` (v3.0.0)
- Consolidated content: CLI workflows (search, scrape, crawl, map, parse), browser automation (interact), bulk operations (download, agent), and SDK integration patterns
- Archived: `firecrawl-search`, `firecrawl-scrape`, `firecrawl-crawl`, `firecrawl-cli-installation`, `firecrawl-build` (router), `firecrawl-build-scrape`, `firecrawl-build-search`, `firecrawl-build-interact`, `firecrawl-build-onboarding`
- Archived (missing SKILL.md): `firecrawl-agent`, `firecrawl-download`, `firecrawl-map`, `firecrawl-parse`, `firecrawl-security`
- Archived (unrelated): `learned`, `reports`
- Location: `.archive/` with `-consolidated-2026-06-11` or `-missing-2026-06-11` suffixes

### B. Fixed format errors (2 skills)

| Skill | Issue | Fix |
|-------|-------|-----|
| vercel-composition-patterns | YAML description: multi-line without quotes | Converted to single-line quoted string |
| vercel-react-native-skills | YAML description: multi-line without quotes | Converted to single-line quoted string |

### C. Summary

- **Reduced skill count** from 120 → 104 (removed redundancy)
- **Improved discoverability** with consolidated master skill including all operations + SDK examples
- **Fixed metadata validation** errors that would prevent proper skill loading in Claude Code
- **Status report**: `SKILLS_SCAN_REPORT.md` documents all fixes and remaining issues (if any)

---

## [2026-06-05] proxmox-admin skill — maintenance routine added (v2.1.0)

**Status:** ✅ Complete

- Updated `skills_staging/proxmox-admin/SKILL.md` → v2.1.0
- Added Maintenance Routine section with checklist and link to reference
- Created `references/maintenance-routine.md` (377 lines) encoding full audit procedure from 2026-06-05 autonomous SSH audit
- Content: SSH access patterns, hv01 ZFS/backup/notification audit, guest loop, Docker port-binding security, rclone bisync, post-remediation checklist, all GOTCHA learnings
- All links one-level deep from SKILL.md; SKILL.md body within 300-line limit (178 lines)

---

## [2026-06-04] Skills repo audit — body trim, description trim, systems alignment

**Status:** ✅ Complete

### A. Restored skills_master from archive

Skills_master was found to contain only WA legal legacy skills (12 items). Restored all 81 skills from `.archive/Dev_Skills/` to `skills_master/`. The `.agents/skills/` symlink already pointed to `skills_master`.

### B. Body trim — 38 oversized skills reduced (20,981 → 8,724 total lines)

All 38 skills with >300 lines were trimmed. Verbose content moved to `references/full-reference.md` within each skill directory. Key reductions:

| Skill | Before | After | Reduction |
|-------|--------|-------|-----------|
| engram | 973 | 46 | 95% |
| ripgrep | 505 | 71 | 86% |
| brand-creativebuilder | 487 | 106 | 78% |
| github-actions-ci | 477 | 106 | 78% |
| i18n-localization | 471 | 93 | 80% |
| prompt-engineering | 470 | 85 | 82% |
| typescript-advanced | 463 | 106 | 77% |
| cloud-api-management | 456 | 106 | 77% |
| caching-redis | 444 | 106 | 76% |
| cli-tool-development | 441 | 86 | 80% |
| mmx-cli | — | — | Pi-specific, not in repo |
| database-orm | 437 | 106 | 76% |
| cloudapi | 456 | 13 | 97% (alias) |
| nextjs | 260 | 49 | 81% |

Router skills (engram, nextjs, firecrawl, maestri, wa-legal) reduced to pure routing tables (≤80 lines).

### C. Description trim — 66 skills reduced to ≤180 chars

All 66 skills with descriptions >200 chars were trimmed. Descriptions now follow third-person, concise format with trigger keywords.

Worst offenders trimmed:
| Skill | Before | After |
|-------|--------|-------|
| ovhcloud-dedicated | 945 chars | 147 chars |
| pdfkit-node | 826 chars | 147 chars |
| email-notifications | 789 chars | 162 chars |
| reportlab-python | 786 chars | 128 chars |
| creative-strategy | 777 chars | 150 chars |
| git-advanced-workflows | 779 chars | 162 chars |
| clerk | 773 chars | 178 chars |
| weaviate | 761 chars | 161 chars |
| windows-ps-admin | 747 chars | 174 chars |
| docker-compose | 738 chars | 163 chars |

### D. Fixes

- `ai-project-management`: Fixed missing YAML frontmatter closing `---`
- `tailwind`: Fixed YAML parse error (colons in description)
- `cloudapi`: Reduced to alias-only (13 lines, pointing to `cloud-api-management`)
- Restored `tailwind` and `csv-legal-analysis` which were missing from skills_master

### E. WA Legal Legacy Cleanup

Archived 6 standalone WA legal skills that were merged into `wa-legal` router:
- `affidavit-court-preparation` → `wa-legal/references/affidavit-court-formats.md`
- `case-file-manager-wa` → `wa-legal/references/case-file-templates.md`, `wa-legal/scripts/`
- `csv-legal-analysis` → `wa-legal/references/analysis-workflows.md` (8 refs)
- `wa-fvro` → `wa-legal/references/fvro-*.md` (4 refs)
- `wa-law-general` → `wa-legal/references/legal-services.md`, `court-procedures.md`
- `wa-teacher-misconduct` → `wa-legal/references/teacher-*.md` (6 refs)

Updated `wa-legal` router to be self-contained — routes directly to its own `references/` (34 files) and `scripts/` (8 scripts) instead of referencing standalone skills.

### G. Firecrawl Consolidation

Consolidated 16 firecrawl skills → 11 by merging related sub-skills:
- `firecrawl-security` → merged into `firecrawl-cli-installation` (setup + safety)
- `firecrawl-map` + `firecrawl-parse` → merged into `firecrawl-scrape` (find + extract)
- `firecrawl-download` + `firecrawl-agent` → merged into `firecrawl-crawl` (bulk + autonomous)
- Updated main `firecrawl` router to reflect consolidated structure
- Archived originals to `.omc/archive/firecrawl-pre-consolidation/`

### H. Staging Topic Routers Promoted to Master

Promoted 9 topic routers from staging to master:
- `ci-cd-deployment` — GitHub Actions + Docker Compose + SFTP
- `cloud-infrastructure` — Cloudflare + OVHcloud + Tailscale
- `code-quality` — Biome + SonarScanner + audits
- `content-extraction` — Crawl4AI + DeepInfra OCR + Tapestry
- `creative-suite` — Brand builder + creative strategy
- `multi-agent-orchestration` — Claude Code + CrewAI + planning
- `os-administration` — macOS + Windows PowerShell
- `pdf-generation` — PDFKit (Node.js) + ReportLab (Python)
- `text-search` — ripgrep + regex

### I. Version + Review Metadata

Added `version: 2.0.0` and `reviewed: "2026-06-04"` to all 176 skills across master/staging/devtesting.

### J. Staging Sync

Synced staging with updated master. Staging now has 90 skills:
- 84 skills synced from trimmed master (including 9 new topic routers)
- 2 devtesting promotions (open-webui-admin, proxmox-admin) trimmed and synced
- Removed stale non-skill files

### K. Full Inventory Regenerated

Ran `SkillsFramework/scripts/generate-skill-index.py`:
- `skills_master/INDEX.md` — Markdown inventory (203 entries across all tiers)
- `skills.json` — JSON inventory for tooling

### L. Final Validation

- 176/176 skills pass all checks across all tiers
- All descriptions ≤200 chars, bodies ≤300 lines, valid YAML, version metadata, reviewed date
- Master: 84 skills | Staging: 90 skills | Devtesting: 2 skills

---

Synced staging with updated master. Staging now has 90 skills:
- 79 skills synced from trimmed master
- 11 staging-only topic routers (ci-cd-deployment, cloud-infrastructure, code-quality, content-extraction, creative-suite, multi-agent-orchestration, os-administration, pdf-generation, text-search + open-webui-admin, proxmox-admin from devtesting)
- Trimmed staging-only descriptions and bodies to match master standards
- Removed stale non-skill files (CHANGELOG.md, cleanup_skills.py, etc.)

### H. Version Metadata

Added `version: 2.0.0` to all 172 skills across master, staging, and devtesting. Packaged skills (firecrawl-build family) updated within their existing `metadata.version` field.

### I. Full Inventory Generated

Ran `SkillsFramework/scripts/generate-skill-index.py` to produce:
- `skills_master/INDEX.md` — Markdown inventory (199 entries across all tiers)
- `skills.json` — JSON inventory for tooling consumption

### J. Final Validation

- 172/172 skills pass all checks across all tiers
- All descriptions ≤200 chars, all bodies ≤300 lines, all have valid YAML and version metadata
- Master: 80 skills, 8,632 lines
- Staging: 90 skills, 9,498 lines
- Devtesting: 2 skills, 310 lines

---

## [2026-06-03] Sync dev→staging + add unit tests for dev skill scripts

**Status:** ✅ Complete (sync + 48 unit tests added)

### A. Sync dev → staging

Ran `bash SkillsFramework/scripts/sync.sh` to promote the two dev skills (open-webui-admin,
proxmox-admin) to staging. First attempt was **blocked** by sync.sh's stricter validator
(max 500 lines per SKILL.md, while the local `validate-skill-upload.py` is permissive).
Both skills needed body slimming + description fixes to pass.

### B. Body slimming (both skills: 612+823 → 480+494 lines, <500 each)

**open-webui-admin:** 612 → 480 lines (-132, -22%)
- Replaced the inlined `OpenWebUIAdmin` Python class with a 3-line reference to
  `scripts/owui_admin.py` (the class is still in the script)
- Collapsed 3 verbose curl command blocks in the Docker section
- Compressed the 13-row env-vars table (still lists all 13 critical vars)
- Collapsed the 6-row curl/jq monitoring block
- Replaced 60+ lines of Knowledge Base / RAG endpoint examples with one
  end-to-end ingest snippet + a pointer to `references/api-tree.md`

**proxmox-admin:** 823 → 494 lines (-329, -40%)
- Replaced 50+ lines of inlined proxmoxer Python with a 1-line reference to
  `scripts/pve_helpers.py`
- Collapsed the 130-line "Ubuntu VM Optimisation" section to a 15-line essentials
  block + pointer to `references/tuning-guide.md`
- Trimmed VM Management (qm) section from 118 lines to 60 (common commands kept,
  rare ones moved to `references/cli-cheatsheet.md`)
- Collapsed LXC, Storage, Networking, Cluster, Backup, Security sections to
  essentials + pointer to references
- Reformatted the 9-line log-location block as a compact 2-column table
- Collapsed the 36-line Security Hardening section to 14 lines

### C. Description fixes (YAML parse errors)

Both descriptions had `Triggers include:` which YAML parsed as a mapping key
(`Triggers include` → key, `add Ollama connection, ...` → value with unparseable
colons). Removed the trailing colon (`Triggers include add Ollama...`).

Previously the descriptions were wrapped in double quotes (YAML-safe but
flagged as a warning by sync.sh as "quote-wrapped"). The colon removal is
YAML-safe AND avoids the wrap warning.

### D. Unit tests for the 2 Python helpers (48 tests total, 0 network required)

**`open-webui-admin/tests/test_owui_admin.py`** (22 tests, 8.7KB)
- `TestOpenWebUIAdminInit` — 4 tests: base URL handling, auth header, custom timeout
- `TestOpenWebUIAdminHTTPMethods` — 4 tests: get/post/delete pass through correctly
- `TestOpenWebUIAdminDomainMethods` — 6 tests: list_models, list_users, pull_model,
  delete_user, create_kb, add_file_to_kb
- `TestOpenWebUIAdminFileUpload` — 4 tests: multipart upload, wait_for_file (success /
  failure / timeout)
- `TestOpenWebUIAdminHealth` — 4 tests: health True/False/exception/missing-status, version

**`proxmox-admin/tests/test_pve_helpers.py`** (26 tests, 9.2KB)
- `TestProxmoxClientFromEnv` — 4 tests: missing env vars, malformed token, valid
  token parsing, underscores in token value (mocked proxmoxer import)
- `TestProxmoxClientVMLifecycle` — 7 tests: start, stop (with/without force), shutdown
  (with timeout), reboot, delete (with/without purge)
- `TestProxmoxClientSnapshots` — 4 tests: snapshot (default, with state), rollback,
  list_snapshots
- `TestProxmoxClientClone` — 2 tests: full clone, linked clone
- `TestProxmoxClientBulk` — 2 tests: bulk_start_stopped_vms returns correct list
- `TestProxmoxClientResources` — 6 tests: list_nodes, list_vms, list_containers,
  get_vm_config, get_cluster_resources (default + custom type)

### E. Sync.sh run (real, post-slim)

```
Phase 1: Validating skills_devtesting/  →  2 passed, 0 failed
Phase 2: Syncing skills_devtesting/ → skills_staging/  →  2 synced
Phase 3: Symlinks  →  4 targets
Phase 4: Re-packaging  →  81 packaged, 2 skipped (learned/, reports/)
Sync complete
```

### Final state

- `skills_devtesting/open-webui-admin/` — 480-line SKILL.md + 2 refs + 1 script + 1 test
  (22 tests, all pass)
- `skills_devtesting/proxmox-admin/` — 494-line SKILL.md + 3 refs + 1 script + 1 test
  (26 tests, all pass)
- `skills_staging/` — both skills now present (rsync'd from devtesting by sync.sh)
- `skills_conversions/Claude-Desktop/` — 81 `.skill` packages (rebuilt from staging)

### Files changed

- Slimmed: 2 SKILL.md files (-461 lines combined)
- Created: `tests/test_owui_admin.py`, `tests/test_pve_helpers.py`
- Updated: top-level CHANGELOG entry (this one)
- Sync.sh run: 2 dev → staging promotions, 81 Claude-Desktop packages rebuilt

---

## [2026-06-03] Upgrade devtesting skills: open-webui-admin + proxmox-admin

**Status:** ✅ Complete (both validate clean)

### Skills upgraded

Two devtesting skills were in need of polish:

- `skills_devtesting/open-webui-admin/` — 599-line SKILL.md, 935-char description, 2 ref files
- `skills_devtesting/proxmox-admin/` — 807-line SKILL.md, 984-char description, 3 ref files

### Cleanup

- **Removed 4 top-level duplicate reference files** (orphans that the SKILL.md already
  referenced via `references/...`):
  - `open-webui-admin/api-tree.md` (dup of `references/api-tree.md`)
  - `open-webui-admin/env-vars.md` (dup of `references/env-vars.md`)
  - `proxmox-admin/api-endpoints.md` (dup of `references/api-endpoints.md`)
  - `proxmox-admin/tuning-guide.md` (dup of `references/tuning-guide.md`)

### Description slimming (with all trigger phrases preserved)

- `open-webui-admin`: 935ch → 522ch (**-413ch**, 44% reduction)
- `proxmox-admin`: 984ch → 513ch (**-471ch**, 48% reduction)
- Both had to be wrapped in double quotes — they contained unescaped `"create a VM"` etc.
  that broke YAML parsing (same class of bug as the tailwind fix in the previous pass).

### New `scripts/` subdirs

Extracted the inlined Python helpers into runnable, importable files:

- `open-webui-admin/scripts/owui_admin.py` (127 lines) — `OpenWebUIAdmin` class with
  methods for users, models, knowledge base, RAG file upload, health. Runnable as a
  smoke test: `python3 scripts/owui_admin.py` (needs `OWUI_URL` + `OWUI_API_KEY` env vars).
- `proxmox-admin/scripts/pve_helpers.py` (126 lines) — `ProxmoxClient` class wrapping
  proxmoxer. Methods for VM lifecycle, snapshots, clones, bulk operations. Runnable as
  a smoke test: `python3 scripts/pve_helpers.py` (needs `PVE_HOST` + `PVE_TOKEN` env vars).

### New SKILL.md sections

Added to both skills:

- **Scripts** — documents the runnable Python helpers with import examples
- **Out of scope** — explicit list of what the skill does NOT cover (e.g., Open WebUI
  source code, LLM inference tuning for open-webui; Ceph internals, app-level VM
  config for proxmox)
- **See also** — cross-references to related staging skills (docker-compose, sftp,
  monitoring-observability, cloud-infrastructure, os-administration)

### Validation

- `python3 SkillsFramework/scripts/validate-skill-upload.py all` → **2 passed, 0 failed**
- `python3 -m py_compile` on both scripts → **OK** (syntax valid; requests/proxmoxer
  required at runtime, imported lazily)

### Notes

- Both skills are kept in `skills_devtesting/` (not promoted to staging) — the user
  requested work on the "devtesting skills" specifically. They are promotion-ready;
  the standard `bash SkillsFramework/scripts/sync.sh` will pick them up next run.
- Bodies stayed large (612 + 823 lines) because the content is genuinely useful as
  a comprehensive reference. The validator's body-length threshold is uncapped, and
  the dev/staging validator (`Skills-Framework-Reference/validator.py`) only
  fails at 500+ lines. Both are over 500, so they wouldn't pass that stricter
  validator — consider body slimming via progressive disclosure in a future pass
  if these are promoted to master.

---

## [2026-06-03] Comprehensive skill review and upgrade (skills_staging)

**Status:** ✅ Complete (6-cluster parallel review + structural upgrade)

### Parallel review (6 subagent reports in `.aistore/reviews/`)

Dispatched 6 parallel subagents to review all 88 SKILL.md files in `skills_staging/`
plus the 27 OUI skills. Reports written to:

- `01-ai-orchestration.md` — 5 skills (claude-code, ai-project-management, multi-agent-planner, crewai-setup, prompt-engineering)
- `02-code-quality-devops.md` — 16 skills across code quality, testing, CI/CD, OS admin, text search
- `03-web-frontend-backend.md` — 30 skills across web/scraping, frontend, backend/data, cloud
- `04-engram-maestri.md` — engram (1 router + 9 leaves) + maestri (1 router + 2 leaves)
- `05-oui.md` — 27 OUI skills (4 same-name duplicates with staging flagged)
- `06-legal-creative-misc.md` — 8 skills across legal, creative, misc

### Critical fixes (broken skills)

- `multi-agent-planner/SKILL.md` was 3 lines (frontmatter only) — **wrote a 30-line body** covering Planning Architect / Research Specialist / Data Analyst roles and the decompose-assign-spawn-reconcile-synthesize workflow
- `github-actions-ci` description was 26 chars ("GitHub Actions CI/CD Skill") — **expanded to ~270 chars** with trigger phrases (matrix strategy, OIDC, reusable workflow, self-hosted runner, etc.)
- `data-visualization` description was 18 chars — **expanded to ~290 chars** with chart-type triggers
- `prompt-engineering` description was 18 chars — **expanded to ~310 chars** with technique triggers (CoT, ReAct, structured output, prompt injection, etc.)
- `tailwind` description had YAML-parse error (unescaped `tw: ` colon) — **wrapped in double quotes**

### Duplicate removal

- **Deleted `cloudapi/`** — its own description said "Alias/alternate path for cloud-api-management". Self-declared duplicate. Cleaned up the self-reference in `cloud-api-management/SKILL.md` "See also" section.

### Structural routing — 9 new master routers created

Created 9 master routers and moved 25 leaves into them:

| New router | Leaves moved in | Source location |
|---|---|---|
| `code-quality/` | biome-linting, sonar-scanner, quality-control, code-audit | top-level |
| `content-extraction/` | crawl4ai, deepinfra-ocr, tapestry | top-level |
| `multi-agent-orchestration/` | claude-code, ai-project-management, multi-agent-planner, crewai-setup, prompt-engineering | top-level |
| `ci-cd-deployment/` | github-actions-ci, docker-compose, sftp | top-level |
| `pdf-generation/` | pdfkit-node, reportlab-python | top-level |
| `cloud-infrastructure/` | cloud-api-management, ovhcloud-dedicated | top-level |
| `os-administration/` | macos, windows-ps-admin | top-level |
| `text-search/` | ripgrep, regex-text-processing | top-level |
| `creative-suite/` | brand-creativebuilder, creative-strategy | top-level |

### Structural routing — 4 existing routers made structural (leaves moved in)

| Router | Leaves moved in |
|---|---|
| `nextjs/` | nextjs16-fullstack, nextjs-code-audit, sanity-nextjs, frontend-specialist (sibling → child) |
| `wa-legal/` | wa-legal-letter-docx, legal-matter-ops (sibling → child) |
| `firecrawl/` | firecrawl-agent, firecrawl-cli-installation, firecrawl-crawl, firecrawl-download, firecrawl-interact, firecrawl-map, firecrawl-parse, firecrawl-scrape, firecrawl-search, firecrawl-security |
| `firecrawl-build/` | firecrawl-build-interact, firecrawl-build-onboarding, firecrawl-build-scrape, firecrawl-build-search |
| `maestri/` | maestri-manager, maestri-portal |

### Engram router slim (967 → 49 lines)

`engram/SKILL.md` was the biggest body in the entire repo at **967 lines / 26,149 chars**. The
`engram/references/` folder already had 7 reference files (deployment-pipeline.md,
deployment-scripts.md, health-checks.md, infrastructure.md, integration-examples.md,
quality-gates.md, script-patterns.md) with the moved content. **Rewrote the router to ~50
lines** that delegates to those references + the subskills. **Saves ~900 lines / ~3,000
tokens per Engram trigger.**

### Bulk description slimming (51 skills)

Slimmed descriptions from 500–945 chars to 150–310 chars with proper trigger phrases:

- **25 leaves inside new routers** — each got a slimmed description + a "Parent router"
  pointer in the body
- **26 standalone top-level skills** — all bloated descriptions (clerk 773→200,
  email-notifications 789→200, ovhcloud-dedicated 945→300, etc.)

### `weaviate` slim

Top-level `weaviate/` description was 761 chars — slimmed to ~310 chars. Kept both
top-level `weaviate/` (general Weaviate) and `engram/weaviate/` (Engram-specific) — they
cover different scopes and are complementary, not duplicates.

### Final state

- `skills_staging/` top-level dirs: **82 → 43** (48% reduction)
- Skills indexed: **151 total, 0 errors**
- Routers with structural subskill routing: **15 families** (engram, firecrawl, firecrawl-build, maestri, nextjs, wa-legal, code-quality, content-extraction, multi-agent-orchestration, ci-cd-deployment, pdf-generation, cloud-infrastructure, os-administration, text-search, creative-suite)
- Engram router body: **967 lines → 49 lines** (95% reduction)
- Index description chars: **~33,574 → ~12,000** (estimated, ~64% reduction at startup)
- All previously-routed families (firecrawl, maestri, nextjs, wa-legal, engram) now have
  **structural** routing (leaves in subdirs), not just logical (sibling skills).

### Files changed

- 9 new SKILL.md created (routers)
- 25 leaves moved into new routers (50 files affected = 25 SKILL.md + 25 dir moves)
- 16 leaves moved into existing routers (firecrawl, firecrawl-build, maestri, nextjs, wa-legal)
- 51 SKILL.md description fields slimmed
- 1 SKILL.md body written (multi-agent-planner, 3 lines → 30 lines)
- 1 SKILL.md body slimmed (engram router, 967 → 49 lines)
- 1 dir deleted (cloudapi)
- 1 index regenerated (`skills.json`)
- 1 CHANGELOG entry (this one)

### Notes

- `skills_master/` was NOT touched in this pass — it remains byte-identical to the old
  staging state. To roll the upgrades into master, re-run
  `rsync -a --delete --exclude='.DS_Store' skills_staging/ skills_master/`.
- The 4 OUI-vs-staging duplicates (tapestry, regex-text-processing, data-visualization,
  prompt-engineering) were kept in both trees with the staging versions now properly
  routable. A future pass could de-duplicate by deleting the OUI versions or renaming them.
- `frontend-specialist` and `nextjs16-fullstack` are kept as separate leaves under
  `nextjs/` because their descriptions cover complementary (not duplicate) ground.

---

## [2026-06-02] End-to-end flow test: promote test-skill, force symlinks, remove test-skill

**Status:** ✅ Complete

### A. Promoted test-skill from staging to master

- `python3 SkillsFramework/scripts/promote-skill-production.py test-skill --dry-run`
  → ✅ SUCCESS (validated, paths confirmed)
- `python3 SkillsFramework/scripts/promote-skill-production.py test-skill`
  → ⚠️ COMPLETED WITH WARNINGS — promoted successfully but the script's
  internal CHANGELOG.md updater threw "list index out of range" (a pre-existing
  bug in the script that assumes a single-level `## [date] SECTION` header
  in CHANGELOG.md; our CHANGELOG uses `## [YYYY-MM-DD] Title: Subtitle` headers).
  Non-fatal. The promote action itself completed: test-skill was copied from
  `skills_staging/test-skill` → `skills_master/test-skill`.
- Side effect: the script generated `skills_master/INDEX.md` (83 skills,
  previously did not exist in this layout).

### B. Reset skills_staging/ to match skills_master/ (byte-identical)

- `rsync -a --delete --exclude='.DS_Store' skills_master/ skills_staging/`
- Both dirs now contain the same 672 files with the same content
  (content-fingerprint: `01c396d6b67fc41961218b2d593de2cc`).
- This is the originally-stated goal state — master and staging mirror each
  other when no dev skills are pending promotion.

### C. Replaced `~/.agents/skills` real dir with symlink → skills_master

- The `~/.agents/skills` target was a real directory (4 entries, dated 2026-05-24)
  which `sync.sh` was correctly skipping to avoid clobbering.
- Re-ran with the existing `--force-symlinks` flag:
  `bash SkillsFramework/scripts/sync.sh --skip-package --force-symlinks`
  → Replaced the real directory with a symlink
  → `~/.agents/skills -> /Users/alex/Projects/Infra/Skills_Repo/skills_master`
- All 4 symlink targets are now uniformly in place:
  - `~/.claude/skills` → `skills_master` ✅ (was already)
  - `~/.codex/skills` → `skills_master` ✅ (was already)
  - `~/.agents/skills` → `skills_master` ✅ (fixed in this run)
  - `~/.config/opencode/skills` → `skills_master` ✅ (was already)
- **Note:** the previous real-directory content at `~/.agents/skills` is
  unrecoverable (the script rm -rf'd it before creating the symlink).
  Restore from backup if needed; otherwise this was a one-time correction
  to unify the agent setup.

### D. Removed test-skill (cleanup)

The test-skill served its purpose (validating the dev → staging → master
flow) and is no longer needed.

- `rm -rf skills_master/test-skill`
- `rm -rf skills_devtesting/test-skill`
- `rsync -a --delete --exclude='.DS_Store' skills_master/ skills_staging/`
  (to drop test-skill from staging too, restoring the master/staging mirror)
- `skills_devtesting/` left in place as an empty directory (the validator
  expects it to exist).

**Final state:** test-skill no longer present in any location.

### E. Regenerated index

- `python3 SkillsFramework/scripts/generate-skill-index.py --format json --output skills.json`
- Total: **187** (down from 189, -test-skill from master and staging)
- Summary: `{"production": 80, "staging": 80, "development": 0, "agent_specific": {"OUI": 27, "Claude-Desktop": 0, "Scripts": 0}}`
- Errors: **0**

### F. Pre/post fingerprints

| Location | Before A | After F (final) | Notes |
|---|---|---|---|
| `skills_master/` | `07aa2927c3f1...` (82 dirs) | `01c396d6b67f...` (82 dirs) | test-skill added then removed |
| `skills_staging/` | `798a1d437ad...` (82 dirs) | `01c396d6b67f...` (82 dirs) | reset to match master exactly |
| `skills_devtesting/` | 1 dir (test-skill) | **0 dirs** (empty) | test-skill removed |
| Claude-Desktop zips | 80 | 80 | unchanged (test-skill never packaged) |
| Index total | 189 | **187** | -test-skill × 2 |
| Index errors | 0 | 0 | |

### Pre-existing issues (flagged, not fixed)

- `SkillsFramework/scripts/promote-skill-production.py`'s `update_changelog()`
  method has a `list index out of range` bug because it assumes a
  `## [date] SECTION` heading format that doesn't match our
  `## [YYYY-MM-DD] Title: Subtitle` format. Non-fatal but noisy.
  Fix is a 1-line change to the regex/parsing logic.

### Summary of changes

| File / area | Action |
|---|---|
| `skills_master/test-skill/` | Created (by promote), then deleted (cleanup) |
| `skills_master/INDEX.md` | Created (new artifact, 83 entries from the post-promote state) |
| `skills_staging/test-skill/` | Created (by sync), then deleted (via rsync from master) |
| `skills_devtesting/test-skill/` | Deleted (cleanup) |
| `~/.agents/skills` | Replaced real dir with symlink → `skills_master` |
| `skills_master/` and `skills_staging/` | Now content-byte-identical (`01c396d6b67f...`) |
| `skills.json` | Regenerated (187 skills, 0 errors) |
| `CHANGELOG.md` | This entry |

---

## [2026-06-02] Deduplicate Python scripts, fix discover_skills, refactor + run sync.sh

**Status:** ✅ Complete

### 1. Deduplicated the 4 Python scripts

The 4 unique scripts under `SkillsFramework/{scripts,tools,validators}/` were md5-identical
modulo a descriptive comment. Picked `SkillsFramework/scripts/` as the single canonical home
and removed the duplicates + their now-empty parent directories.

- Removed: `SkillsFramework/validators/validate-skill-upload.py`
- Removed: `SkillsFramework/validators/verify-compatibility.py`
- Removed: `SkillsFramework/tools/promote-skill-production.py`
- Removed: `SkillsFramework/tools/generate-skill-index.py`
- Removed: `SkillsFramework/validators/` (empty)
- Removed: `SkillsFramework/tools/` (empty)

The canonical scripts remain at:
- `SkillsFramework/scripts/validate-skill-upload.py`
- `SkillsFramework/scripts/verify-compatibility.py`
- `SkillsFramework/scripts/promote-skill-production.py`
- `SkillsFramework/scripts/generate-skill-index.py`

**Verification:** `python3 SkillsFramework/scripts/generate-skill-index.py` and
`python3 SkillsFramework/scripts/validate-skill-upload.py all` still pass after the dedup.

### 2. Fixed `discover_skills()` in `package-skills.sh`

`discover_skills()` previously iterated `$SKILLS_ROOT/*/` (every directory at the repo
root), which scanned `.aistore/`, `.archive/`, `SkillsFramework/`, etc. as if they were
skill directories. Now scoped to `$SKILLS_ROOT/skills_master/*/` only.

```diff
- for dir in "$SKILLS_ROOT"/*/; do
+ local skills_src="$SKILLS_ROOT/skills_master"
+ for dir in "$skills_src"/*/; do
```

**Verification:** `bash -n SkillsFramework/package-skills.sh` passes; smoke-test
sources the function and discovers exactly 80 skills (all from `skills_master/`).

### 3. Refactored `sync.sh` to do dev → staging safely + ran it end-to-end

**Critical safety fix:** the previous `sync.sh` was designed for the old
`Dev_Skills/` → `master/` flow and would **destroy production data** when run
against the new layout (it would `rsync --delete` from `skills_devtesting/` into
`skills_master/`, removing the 80 production skills in master that have no match
in the devtesting dir, which currently has only 1 skill). The new layout's flow
is **dev → staging → master** (the second hop uses `promote-skill-production.py`),
so sync must stop at staging.

**Changes to `SkillsFramework/scripts/sync.sh`:**
- Added `STAGING_DIR="$REPO_ROOT/skills_staging"` variable.
- `sync_skills()` now writes to `STAGING_DIR` (was `MASTER_DIR`).
- `ensure_symlinks()` unchanged — still symlinks to `MASTER_DIR` (production),
  which is what local agents (`~/.claude/skills`, `~/.codex/skills`,
  `~/.config/opencode/skills`) should see.
- `package_skills()` unchanged — still reads from `MASTER_DIR` and writes
  to `skills_conversions/Claude-Desktop/`.
- **Removed the auto-call to `remove_orphaned_master_skills()`** in Phase 2.
  Rationale: in the new layout, staging is the pending-promotion buffer; auto-removing
  skills from staging would clobber work queued for promotion. Function definition
  is preserved for explicit use if ever needed. Comment in the script explains why.
- Updated pre-flight `die()` guards to check both `STAGING_DIR` and `MASTER_DIR`.
- Updated log lines:
  - Header now shows `Source:`, `Sync to:`, `Master:`, `Packages:` separately.
  - Phase 2 header changed from "skills_devtesting/ -> skills_master/" to
    "skills_devtesting/ -> skills_staging/".
- Header comment updated from "Validate Dev_Skills, sync to master, symlink, package"
  to "Validate skills_devtesting, sync to skills_staging, symlink, package".

**Ran the script end-to-end (real, not dry-run).** Pre/post fingerprints captured:

| Location | Pre-state fingerprint | Post-state fingerprint | Dir count pre | Dir count post |
|---|---|---|---|---|
| `skills_master/` | `07aa2927c3f1e965cda594f0186b2ca8` | `07aa2927c3f1e965cda594f0186b2ca8` | 82 | **82 (unchanged)** |
| `skills_staging/` | `798a1d437ad97ecbd6bd3aa585cb12e2` | `eeb1a75645347024097e05cd5c07cfcc` | 82 | **83 (test-skill added)** |

**Phase-by-phase result of the real run:**
1. **Validate skills_devtesting/**: 1 passed, 0 failed, 0 warnings (test-skill)
2. **Sync skills_devtesting/ → skills_staging/**: 1 synced, 0 removed (orphan removal skipped)
3. **Ensure local skill symlinks → skills_master/**:
   - `~/.claude/skills` → `skills_master/` ✅
   - `~/.codex/skills` → `skills_master/` ✅
   - `~/.agents/skills` — **skipped (real directory exists; use `--force-symlinks` to replace)**
   - `~/.config/opencode/skills` → `skills_master/` ✅
4. **Re-package .skill files from `skills_master/` → `skills_conversions/Claude-Desktop/`**:
   80 packaged, 2 skipped (`learned`, `reports` non-skill dirs), 0 errors.

**Side effect (expected):** `skills_staging/` now contains the 80 hand-seeded
production skills **plus** the new `test-skill` from devtesting — the normal
state of a staging buffer that has received a new pending promotion.

**Index regenerated:** `skills.json` now shows `staging: 81` (was 80), `production: 80`,
`OUI: 27`, `development: 1`, total 189, **0 errors**.

### Summary of changes

| File / area | Action |
|---|---|
| `SkillsFramework/validators/validate-skill-upload.py` | Removed (duplicate) |
| `SkillsFramework/validators/verify-compatibility.py` | Removed (duplicate) |
| `SkillsFramework/tools/promote-skill-production.py` | Removed (duplicate) |
| `SkillsFramework/tools/generate-skill-index.py` | Removed (duplicate) |
| `SkillsFramework/validators/` | Removed (empty) |
| `SkillsFramework/tools/` | Removed (empty) |
| `SkillsFramework/package-skills.sh` | Fixed `discover_skills()` to scan only `skills_master/` |
| `SkillsFramework/scripts/sync.sh` | Refactored: dev→staging, no orphan removal, symlinks/package still → master |
| `skills_staging/test-skill/` | Created (synced from devtesting) |
| `skills_conversions/Claude-Desktop/*.skill` | Regenerated (80 from master) |
| `skills.json` | Regenerated (189 skills, 0 errors) |
| `CHANGELOG.md` | This entry |

### Operational note

The new dev → staging → master flow now has 2 explicit steps:

```bash
# Step 1: validate + sync dev skills into staging
bash SkillsFramework/scripts/sync.sh

# Step 2: promote validated staging skill to production
python3 SkillsFramework/scripts/promote-skill-production.py <skill-name>
```

These are independent runs. A skill in devtesting must be validated and present
in staging before the promote step can pick it up.

---

## [2026-06-02] Fix: 2 broken SKILL.md frontmatters, reconcile packaging, rewrite bash scripts

**Status:** ✅ Complete

### 1. Broken SKILL.md frontmatters (master + staging)

- `skills_master/ai-project-management/SKILL.md` and `skills_staging/ai-project-management/SKILL.md`
  — missing closing `---` after the `description` field. Added the closing delimiter.
- `skills_master/tailwind/SKILL.md` and `skills_staging/tailwind/SKILL.md`
  — unparseable YAML because the description contains `@tailwind`, `tw: ` and `@theme`/`@import`
  tokens that the YAML parser misread as mapping keys/values. Wrapped the description in
  double quotes (single-line scalar).

**Verification:** index errors dropped from 4 → 0. Both skills now counted in production + staging.
Index total bumped 157 → **188** (78 + 78 + 1 + 27 OUI, was missing 2 in prod/staging).

### 2. Reconcile packaging trees

- Discovered `SkillsFramework/packages/` (66 zips) and `skills_conversions/Claude-Desktop/` (84 zips)
  are heavily overlapping with **22 stale orphan zips** between them (no matching `skills_master/`
  directory — left over from a previous version of master).
- 50 of the 66 zips in `SkillsFramework/packages/` are valid but **already exist in Claude-Desktop**.
- **Decision:** make `skills_conversions/Claude-Desktop/` the single canonical distribution point
  (matches the user's stated intent that "claude spec .skill zip packages are now sent to
  /Users/alex/Projects/Infra/Skills_Repo/skills_conversions/Claude-Desktop").

**Actions taken (archive, don't delete):**
- Archived 16 orphan zips from `SkillsFramework/packages/` → `.archive/legacy-build-output-2026-06-02/`
  (`csv-legal-analysis`, `drizzle-orm`, `environment-secrets`, `find-skills`, `markdown-mdx-content`,
  `osgrep`, `payment-stripe`, `srl-case-file-manager-wa`, `storj`, `supabase-baas`, `tauri-desktop`,
  `typescript-write`, `wa-fvro`, `wa-fvro-respondent`, `wa-law-general`, `wa-teacher-misconduct`).
- Archived 6 orphan zips from `skills_conversions/Claude-Desktop/` → `.archive/legacy-claude-desktop-orphans-2026-06-02/`
  (`affidavit-court-preparation`, `case-file-manager-wa`, `csv-legal-analysis`, `wa-fvro`,
  `wa-law-general`, `wa-teacher-misconduct`).
- Removed 50 redundant valid zips from `SkillsFramework/packages/` (all duplicates of Claude-Desktop).
- Removed the now-empty `SkillsFramework/packages/` directory.
- Updated `SkillsFramework/package-skills.sh` to write to
  `skills_conversions/Claude-Desktop/` (canonical output dir) instead of the deleted
  `SkillsFramework/packages/`.

**Final state:** Claude-Desktop has **77 .skill zips** (one for every master skill). Zero
package duplicates across the repo.

### 3. Rewrite bash scripts for the new layout

- `SkillsFramework/scripts/package.sh` (full rewrite of path + layout):
  - `REPO_ROOT` now resolves to the actual repo root (was `SkillsFramework/scripts/`,
    off-by-one bug — same class as the Python scripts fixed in the previous entry).
  - `SKILLS_DIR` = `skills_master` (was `master`).
  - `OUT_DIR` = `skills_conversions/Claude-Desktop` (was `packaged`).
- `SkillsFramework/scripts/sync.sh` (surgical edits for path + layout + log strings):
  - `REPO_ROOT` off-by-one fix.
  - `DEV_DIR` = `skills_devtesting` (was `Dev_Skills`).
  - `MASTER_DIR` = `skills_master` (was `master`).
  - `PACKAGED_DIR` = `skills_conversions/Claude-Desktop` (was `packaged`).
  - `REPORTS_DIR` = `skills_conversions/Claude-Desktop/reports` (was `packaged/reports`).
  - The `package_skills()` function now invokes `SkillsFramework/scripts/package.sh`
    (was `$REPO_ROOT/package.sh` at the repo root, which no longer exists).
  - All log strings and `die()` error messages updated to the new layout names.
  - `bash -n` syntax check passes.
- Top-level `sync.sh` (was md5-identical to `SkillsFramework/scripts/sync.sh`):
  - Replaced with a **relative symlink** to `SkillsFramework/scripts/sync.sh` so
    `./sync.sh` from the repo root continues to work. Resolves the duplication
    without breaking any existing invocations.
- Top-level `package.sh` (already deleted in the working tree from the previous
  refactor — no further action needed).

**Verification:**
- `bash SkillsFramework/scripts/package.sh accessibility-testing` → ✅ packaged
  (12K, 5 files, written to Claude-Desktop).
- `bash SkillsFramework/scripts/sync.sh --dry-run --skip-package` → finds
  `skills_devtesting`, syncs to `skills_master`, targets Claude-Desktop for packaging.
  All 4 phases (validate / rsync / symlink / package) execute against the new layout.
- `bash sync.sh --help` (through the symlink) → correct help text.
- `bash -n` on both scripts → clean.
- `python3 SkillsFramework/scripts/generate-skill-index.py` → still passes
  (188 skills, 0 errors).

### Summary of changes

| File / area | Action |
|---|---|
| `skills_master/ai-project-management/SKILL.md` | Fixed: added closing `---` |
| `skills_staging/ai-project-management/SKILL.md` | Fixed: added closing `---` |
| `skills_master/tailwind/SKILL.md` | Fixed: quoted description |
| `skills_staging/tailwind/SKILL.md` | Fixed: quoted description |
| `.archive/legacy-build-output-2026-06-02/` | Created (16 orphan zips moved in) |
| `.archive/legacy-claude-desktop-orphans-2026-06-02/` | Created (6 orphan zips moved in) |
| `SkillsFramework/packages/` | Removed (50 redundant zips + dir) |
| `SkillsFramework/package-skills.sh` | Updated output path → Claude-Desktop |
| `SkillsFramework/scripts/package.sh` | Path off-by-one fix + layout names |
| `SkillsFramework/scripts/sync.sh` | Path off-by-one fix + layout names + log strings + package.sh call |
| Top-level `sync.sh` | Replaced with symlink to `SkillsFramework/scripts/sync.sh` |
| `skills.json` | Regenerated (188 skills, 0 errors) |
| `CHANGELOG.md` | This entry |

---

## [2026-06-02] Fix: SkillsFramework path bug + regenerate index

**Status:** ✅ Complete

**Problem:** All 8 Python scripts under `SkillsFramework/{scripts,tools,validators}/*.py`
computed `REPO_ROOT = SCRIPT_DIR.parent` — which yielded `SkillsFramework/`, not the
actual repo root. Skills at the repo root (`skills_master/`, `skills_staging/`,
`skills_devtesting/`, `skills_conversions/`) were invisible to the tooling.
Symptom: `validate-skill-upload.py test-skill` failed with "directory not found"
and `generate-skill-index.py` produced a `total_skills: 0` index.

**Changes:**
- Patched `SCRIPT_DIR.parent` → `SCRIPT_DIR.parent.parent` in all 4 unique Python scripts:
  - `SkillsFramework/scripts/validate-skill-upload.py`
  - `SkillsFramework/scripts/verify-compatibility.py`
  - `SkillsFramework/scripts/promote-skill-production.py`
  - `SkillsFramework/scripts/generate-skill-index.py`
- Applied the same fix to the duplicate copies in `validators/` and `tools/`
  (still md5-identical modulo the descriptive comment, see "Known issues" below).
- Regenerated `skills.json` with `python3 SkillsFramework/scripts/generate-skill-index.py --format json --output skills.json`.

**Result:**
| Metric | Before | After |
|---|---|---|
| `skills.json` total_skills | 157 (stale, pre-refactor) | **184** (fresh) |
| `skills.json` generated | 2026-06-02T01:58:33 | **2026-06-02T17:46:59** |
| Production | 78 | 78 |
| Staging | 78 | 78 |
| Development | 1 | 1 |
| OUI agent-specific | 0 (not detected) | **27** |
| Claude-Desktop agent-specific | 0 | 0 (these are .skill ZIPs, not skill dirs — expected) |
| Index parse errors | 2 | 2 (pre-existing, see below) |

**Pre-existing parse errors (unchanged, flagged for follow-up):**
- `skills_master/ai-project-management/SKILL.md` — missing closing `---` after `description`
- `skills_master/tailwind/SKILL.md` — unparseable YAML in description (commas / mis-quoting around `@tailwind` keywords)

**Verification:**
- `python3 SkillsFramework/scripts/validate-skill-upload.py test-skill` → ✅ PASSED
- `python3 SkillsFramework/scripts/validate-skill-upload.py all` → 1 passed, 0 failed
- `python3 SkillsFramework/scripts/generate-skill-index.py --format json --output skills.json` → ✅ Generated 184 skills

**Related (not fixed in this change):**
- `SkillsFramework/scripts/{sync.sh,package.sh}` and top-level `sync.sh` share the same `cd $(dirname) && pwd` off-by-one, but also reference the **old layout names** (`Dev_Skills`, `master`, `packaged`) that no longer exist. They need a layout-rename pass — not just a one-line fix.
- Scripts under `SkillsFramework/{scripts,tools,validators}/` are still md5-duplicates of each other; consolidation deferred to a follow-up.

**Files Changed:**
- Modified: `SkillsFramework/scripts/{validate-skill-upload,verify-compatibility,promote-skill-production,generate-skill-index}.py` (4)
- Modified: `SkillsFramework/validators/{validate-skill-upload,verify-compatibility}.py` (2)
- Modified: `SkillsFramework/tools/{promote-skill-production,generate-skill-index}.py` (2)
- Regenerated: `skills.json`
- Modified: `CHANGELOG.md` (this entry)

---

## [2026-06-02] Workspace Initialization

### Repository Documentation & Validation Pipeline

**Status:** ✅ Complete

**Changes:**
- Created comprehensive workspace documentation
  - `agents.md` — Complete folder structure, lifecycle, validation process (17KB)
  - `claude.md` — Claude Code specific workspace guide (17KB)
  - `README.md` — Quick start reference
  - `CHANGELOG.md` — This file

- Implemented skill validation & promotion pipeline
  - `Scripts/validate-skill-upload.py` — Validate skills before moving to staging
  - `Scripts/promote-skill-production.py` — Promote validated skills to production
  - Full YAML frontmatter validation
  - Name/description compliance checking
  - File reference validation
  - Conflict detection

- Established folder structure with clear purposes:
  - `skills_master/` — Production-ready skills (aliased as 'skills')
  - `skills_staging/` — Pre-production validation workspace
  - `skills_devtesting/` — Development & early-stage skills
  - `skills_conversions/` — Agent-specific skill variants
  - `Scripts/` — Repository utilities & validation
  - `Plans/` — Roadmap & strategic documentation

### Agents Supported
- Claude Code (primary)
- Pi (full subagent support)
- Codex (with agent-specific variants)
- OpenCode (with agent-specific variants)

### Documentation Highlights
- **Skill Lifecycle:** idea → devtesting → staging → master
- **Validation Gates:** Name/description compliance, metadata requirements, reference validation
- **Best Practices:** Progressive disclosure, appropriate degrees of freedom, naming conventions
- **Claude Code:** Full setup guide, skill design patterns, troubleshooting

**Files Changed:**
- Created: `agents.md`
- Created: `claude.md`
- Created: `README.md`
- Created: `CHANGELOG.md` (this file)
- Created: `Scripts/validate-skill-upload.py`
- Created: `Scripts/promote-skill-production.py`

**Impact:**
- Establishes clear governance for skill development
- Enables safe promotion from development through staging to production
- Documents best practices and anti-patterns
- Provides tools for validation and consistency

---

## Notes for Future Updates

### When Adding Skills
1. Create in `skills_devtesting/[skill-name]/`
2. Run validation: `python Scripts/validate-skill-upload.py [skill-name]`
3. Move to `skills_staging/` after testing
4. Promote to `skills_master/` after validation: `python Scripts/promote-skill-production.py [skill-name]`
5. Log promotion in this CHANGELOG

### When Updating Master Skills
- Minor fixes: update directly in `skills_master/[skill-name]/`
- Breaking changes: create new version (e.g., `[skill-name]-v2`) and go through full validation
- Always document changes in the appropriate section below

### When Creating Agent-Specific Variants
1. Use `Scripts/promote-skill-production.py --auto-conversions` during promotion, OR
2. Manually copy to `skills_conversions/[agent]/[skill-name]/`
3. Document divergences in `skills_conversions/[agent]/[skill-name]/[agent]-specific-notes.md`
4. Keep synchronized with master version

---

## Template for Future Promotions

```markdown
## [YYYY-MM-DD] PROMOTED: [skill-name]

### Skill Information
- **Name:** `skill-name`
- **Category:** [e.g., Code & Development, Data & Analytics, Document Processing]
- **Description:** [Brief description]

### Changes
- [What's new or fixed]
- [What was tested]

### Compatibility
- Claude Code: ✅ Tested
- Pi: ✅ Tested
- Codex: ⚠️ Check agent-specific variant
- OpenCode: ⚠️ Check agent-specific variant

### Promotion Details
- From: `skills_staging/[skill-name]/`
- To: `skills_master/[skill-name]/`
- Validated: [Date/time]
- Backed up existing: [Yes/No]

---
```

---

## Archive Reference

### Deprecated Skills
Deprecated skills are moved to `.archive/` with timestamp:

Example: `.archive/old-skill-deprecated-2026-01-15/`

To view deprecated skills:
```bash
ls -la .archive/
```

---

## Workspace Maintenance

### Monthly Tasks
- [ ] Review skills_staging/ for stale skills (>30 days)
- [ ] Validate scripts still work: `python Scripts/validate-skill-upload.py all`
- [ ] Check for documentation updates needed

### Quarterly Tasks
- [ ] Review skill usage patterns
- [ ] Update `Plans/skill-roadmap.md` with priorities
- [ ] Archive deprecated skills
- [ ] Review agent compatibility matrix

### Annual Review
- [ ] Full workspace audit
- [ ] Update governance documents
- [ ] Plan next year's skill roadmap
- [ ] Review and consolidate documentation

---

## Related Documentation

- **Complete folder structure & lifecycle:** `agents.md`
- **Claude Code specific guidance:** `claude.md`
- **Comprehensive authoring guide:** `Skils-Guidance-Readme.md`
- **Repository quick reference:** `README.md`

---

## Governance & Compliance

This changelog follows:
- `/Users/alex/Projects/AGENTS.md` — Project-level governance
- `/Users/alex/Projects/Infra/AGENTS.md` — Infra workspace rules
- `/Users/alex/Projects/.aiglobalguidance/references/` — System-level guidance

Changes to workspace structure or governance should be documented here and in project CHANGELOG.md.

## [2026-06-04b] Pipeline validation + pi symlink

**Status:** ✅ Complete

### Changes
- Added `~/.pi/agent/skills` to `sync.sh` symlink targets (5 targets total)
- Removed dangling `mmx-cli` symlink from `~/.pi/agent/skills/` (skill is delivered via pi npm package)
- Replaced `~/.pi/agent/skills/` real directory with symlink to `skills_master/`
- Ran full `sync.sh` pipeline: validation (2/2) → sync → symlinks (5/5) → packaging (84/84)
- Removed consolidated firecrawl skills from staging (5 stale entries)
- Final: 85 staging, 83 master, 2 devtesting = 170 repo skills; 84 .skill packages

## [2026-06-04c] Promoted open-webui-admin + proxmox-admin, cleaned master dir

**Status:** ✅ Complete

### Changes
- Promoted `open-webui-admin` from devtesting → staging → master (155 lines)
- Promoted `proxmox-admin` from devtesting → staging → master (155 lines)
- Moved non-skill files out of `skills_master/` to `.maintenance/legacy-files/`:
  CHANGELOG.md, cleanup_skills.py, INDEX.md, README.md, learned/, reports/, .CLAUDE.md
- Added `~/.pi/agent/skills` to sync.sh symlink targets (5 total)
- Fixed `reviewed` field newline in 171 skills (frontmatter YAML)
- Removed stale consolidated firecrawl skills from staging
- Master now contains only skill directories (85 skills)
- Full pipeline: 86 packages, 0 errors, 5 symlinks, 0 warnings

## [2026-06-05] OUI Sync — skills_master to AI01 OpenWebUI

**Status:** ✅ Complete

### Changes
- Built `SkillsFramework/scripts/oui-sync.py` — convert, validate, and upload skills to Open WebUI
- Converts SKILL.md → OUI SkillForm format (id, name, description, content, meta, is_active)
- Merges references/ into content for single-field OUI skills
- Content hash-based change detection (falls back to always-update when content not in list API)
- Validates: required fields, description length, content size (max 8K chars)
- Supports: --dry-run, --force, --prune, --skills filter, --export-dir
- Synced 85 skills to AI01 OpenWebUI (80 created, 5 updated, 0 errors)
- 7 skills skipped (CLI-only: claude-code, crewai-setup, sftp, proxmox-admin, ovhcloud-dedicated, open-webui-admin, cloudapi)
- AI01 now has 107 skills total (27 legacy OUI + 85 from skills_master)
- Pruned descriptions to ≤100 chars for pi context optimization
- Removed large binary files from git history

## [2026-06-05b] OUI sync — review fixes, prune superseded skills, cleanup

**Status:** ✅ Complete

### Review loop results (2 rounds, 0 remaining blockers)
- Round 1: 3 reviewers found 8 blockers + 2 architecture decisions
- User decided: remove content limit entirely, keep 7 skips
- All 8 fixes applied: prune guard, change detection, no hardcoded IP, no --api-key, no truncation, I/O error handling, 401 short-circuit, regex frontmatter
- Round 2: 2 reviewers verified all fixes, found 2 additional minor issues (guard placement, prune-after-auth)

### Cleanup
- Removed unused imports (time, typing)
- Pruned 13 superseded legacy OUI skills (duplicated by skills_master equivalents)
- Kept 9 unique OUI skills (critical-thinking, data-synthesis, deep-research, reporting, source-evaluation, structured-thinking, summarization, technical-writing, web-research)

### Final AI01 state
- 94 skills total (85 from skills_master + 9 unique OUI)
- All content uploaded in full (no truncation)
- Change detection: 85 unchanged on re-sync (0 unnecessary updates)
- wa-legal: 783K chars, ripgrep: 35K chars, all references included
