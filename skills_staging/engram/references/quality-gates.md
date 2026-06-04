### Pre-Deployment Checklist

- [ ] All tests pass: `scripts/quality-gate.sh`
- [ ] Bundle size <5MB: checked in quality-gate.sh
- [ ] Environment file validated: `Engram-Platform/scripts/validate-env.sh .env`
- [ ] SSL certificates valid (prod): >30 days until expiry
- [ ] Backup created before deployment
- [ ] Tailscale connectivity verified: `tailscale status | grep -E "dv-syd|acdev"`
- [ ] Docker daemon running on target host
- [ ] Disk space available: >10GB on `/` and `/var/lib/docker`
- [ ] No other deployments in progress

---

## Quality Gates

### Platform Quality Gate (`scripts/quality-gate.sh`)

Runs all linters, builds, and tests across the monorepo:

```bash
cd /Users/alex/Projects/Dev/LIVE/Production/09_EngramPlatform
scripts/quality-gate.sh
```

**Coverage:**

1. **MCP Server** (TypeScript)
   - Build: `npm run build`
   - Lint: `npx @biomejs/biome check src/`
   - Tests: `npm test` (382+ pass expected)

2. **Platform Frontend** (Next.js 15)
   - Build: `npm run build`
   - Type check: `npx tsc --noEmit`
   - Lint: `npx @biomejs/biome check src/ app/`
   - Tests: `npm run test:run` (511+ pass expected)

3. **AI Memory** (Python + TypeScript)
   - Python lint: `python -m ruff check app/`
   - Type check: mypy (via `make lint`)
   - Tests: pytest (901+ pass expected, skipped in CI if redis/weaviate offline)

4. **AI Crawler** (Python)
   - Lint: `python -m ruff check app/`
   - Tests: pytest (2393+ pass expected)

5. **Shell Scripts**
   - ShellCheck: `shellcheck -S warning *.sh`

6. **Bundle Size**
   - Check: `.next/static/chunks/*.js` total <5MB uncompressed
   - Threshold: 5242880 bytes (5.0 MB)
   - Warning issued if exceeded, but gate does not fail

7. **Smoke Tests**
   - Conditional: only if Docker services running
   - Runs: `Engram-Platform/scripts/smoke-test.sh`

**Exit Codes:**
- `0`: All gates passed
- `1`: Any gate failed (stops at first failure)

---

