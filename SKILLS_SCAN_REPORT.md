# Skills Scan Report - Format Errors

**Generated:** 2026-06-11  
**Scanned:** 123 skills in `skills_master/`

---

## Summary

| Category | Count | Severity |
|----------|-------|----------|
| Missing SKILL.md files | 7 | High |
| Missing description field | 2 | High |
| Invalid description format | 2 | High |
| Broken file references | 23+ | Medium |

---

## 1. Missing SKILL.md Files (7 total)

These directories exist but have no SKILL.md file. They won't load in Claude Code.

- `firecrawl-agent/`
- `firecrawl-download/`
- `firecrawl-map/`
- `firecrawl-parse/`
- `firecrawl-security/`
- `learned/`
- `reports/`

**Fix:** Either create SKILL.md for each, or move these directories to `.archive/` if they're deprecated.

---

## 2. Missing Description Field (2 skills)

These SKILL.md files are missing the required `description:` field entirely.

- `vercel-composition-patterns/SKILL.md`
- `vercel-react-native-skills/SKILL.md`

**Issue:** The frontmatter shows multi-line descriptions starting on the next line without quotes. YAML parsing treats these as missing the field.

**Example (wrong):**
```yaml
---
name: vercel-composition-patterns
description:
  React composition patterns that scale. Use when refactoring...
---
```

**Fix:** Add quotes around multi-line descriptions:
```yaml
---
name: vercel-composition-patterns
description: "React composition patterns that scale. Use when refactoring components with boolean prop proliferation, building flexible component libraries, or designing reusable APIs."
---
```

---

## 3. Broken File References (23+ skills affected)

Skills reference files that don't exist. Claude Code can't navigate these links.

### By Severity

**Critical (missing other skills):**
- `firecrawl-build-interact/` → missing `../firecrawl-build-scrape/SKILL.md`, `../firecrawl-build-search/SKILL.md`, `../firecrawl-build/SKILL.md`
- `firecrawl-build-onboarding/` → missing `../firecrawl-build-scrape/SKILL.md`
- `firecrawl-build-scrape/` → missing `../firecrawl-build-interact/SKILL.md`
- `firecrawl-build-search/` → missing `../firecrawl-build-interact/SKILL.md`
- `firecrawl-crawl/` → missing `../firecrawl-download/SKILL.md`
- `firecrawl-interact/` → missing `../firecrawl-agent/SKILL.md`
- `firecrawl-scrape/` → missing `../firecrawl-download/SKILL.md`
- `firecrawl-search/` → missing `../firecrawl-crawl/SKILL.md`
- `multi-agent-orchestration/` → missing `../code-quality/SKILL.md`
- `wa-legal-letter-docx/` → missing `../legal-matter-ops/SKILL.md`, `../firecrawl-*` refs, `../nextjs/SKILL.md`, `../wa-legal/SKILL.md`

**Medium (missing reference files):**
- `accessibility-testing/` → missing `references/automated-testing.md`, `references/manual-testing.md`
- `cli-tool-development/` → missing `references/distribution.md`, `references/ink-react-cli.md`
- `compliance-gdpr-privacy/` → missing `references/cookie-consent.md`, `references/data-mapping.md`
- `documentation-site/` → missing `references/api-reference.md`, `references/docusaurus-setup.md`, `references/nextra-setup.md`, `./next-guide.md`
- `email-notifications/` → missing `references/deliverability.md`, `references/notification-systems.md`, `references/react-email.md`
- `feature-flags/` → missing `references/implementation-patterns.md`, `references/testing-with-flags.md`
- `git-advanced-workflows/` → missing `references/advanced-git.md`
- `i18n-localization/` → missing `references/next-intl-advanced.md`
- `open-webui-admin/` → missing `references/full-reference.md`
- `performance-profiling/` → missing `references/bundle-optimization.md`, `references/runtime-profiling.md`
- `proxmox-admin/` → missing `references/full-reference.md`
- `pwa-offline-first/` → missing `references/push-notifications.md`, `references/workbox-patterns.md`
- `typescript-advanced/` → missing `references/advanced-generics.md`, `references/type-challenges.md`
- `vercel-optimize/` → missing `references/candidates.md`

**Fix:** Either create the missing files or remove the references from SKILL.md.

---

## Recommended Actions (Priority Order)

1. **Delete or archive empty directories** (firecrawl-agent, firecrawl-download, etc.)
   - Move to `.archive/` with date suffix if keeping for history
   - Or delete if truly unused

2. **Fix description field formatting** (2 skills)
   - Add quotes around multi-line descriptions
   - Or condense to single line

3. **Clean up broken cross-skill references**
   - Remove `../firecrawl-*/` references if those skills are being deleted
   - Remove `../legal-matter-ops/` reference from `wa-legal-letter-docx/` if not needed
   - Remove `../code-quality/` reference from `multi-agent-orchestration/` if not needed

4. **Create missing reference files** (23 files)
   - Decide which skills are in active use
   - Create stub files for critical references
   - Or remove unused references

---

## Next Steps

1. Run validation script after fixes:
   ```bash
   python Scripts/validate-skill-upload.py [skill-name]
   ```

2. Decide on firecrawl-* skills:
   - Are they active? If so, create SKILL.md files
   - If not, archive them

3. Update CHANGELOG.md with changes made

