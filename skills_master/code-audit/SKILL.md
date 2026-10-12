---
name: code-audit
description: Runs comprehensive security audits, vulnerability scanning, secrets detection, dependency checks, and code quality assessment for application codebases. Use when asked to audit code, review code quality or architecture, scan for vulnerabilities or exposed secrets, check dependencies for CVEs, assess performance or compliance risk, or produce a prioritized remediation plan.
version: "1.0.0"
---

<essential_principles>
## How Code Auditing Works

### Principle 1: Multi-Layer Analysis

Effective audits examine code at multiple levels:
- **Security**: Vulnerabilities, dependencies, secrets exposure
- **Code Quality**: Complexity, duplication, maintainability
- **Architecture**: Design patterns, coupling, cohesion
- **Performance**: Bottlenecks, inefficient algorithms
- **Compliance**: Licensing, regulatory requirements

### Principle 2: Automated + Manual Review

Balance automation with human judgment:
- **Automated**: Security scans, static analysis, dependency checks
- **Manual**: Architecture review, business logic validation
- **Combined**: Use tools to find issues, humans to assess impact

### Principle 3: Risk-Based Prioritization

Not all issues are equal:
- **Critical**: Security vulnerabilities, data exposure, production bugs
- **High**: Performance issues, architectural flaws
- **Medium**: Code smells, minor bugs
- **Low**: Style issues, documentation gaps

### Principle 4: Context Matters

Consider:
- Is this production code or a prototype?
- What's the blast radius if this fails?
- What's the business criticality?
- What are the regulatory requirements?

## 2025 Critical Security Updates

### Next.js / React Server Components RCE (React2Shell, CVE-2025-55182)

A critical remote code execution vulnerability affects React Server Components. Checked 2026-10-12 against the React and Kudelski Security advisories (see sources below).

| Component | Patched release(s) |
|-----------|--------------------|
| Next.js 16.x App Router | 16.0.7 |
| Next.js 15.x App Router | 15.5.7, 15.4.8, 15.3.6, 15.2.6, 15.1.9, 15.0.5 |
| React `react-server-dom-*` packages (19.0 to 19.2 line) | 19.0.3, 19.1.4, 19.2.3 (updated advisory, per Zscaler; the first fixes 19.0.1, 19.1.2 and 19.2.1 were reported as incomplete) |

CVE-2025-66478 is Next.js's own advisory ID; the NVD rejected it as a duplicate of CVE-2025-55182. Check the official Next.js advisory for patch releases published after this check.

**IMMEDIATE ACTION REQUIRED:**
- Upgrade to the patched release for your Next.js line (at least 16.0.7 on 16.x) if you use App Router with React Server Components
- If upgrade is not possible, implement WAF rules blocking malicious requests

Sources: Zscaler ThreatLabz, "React2Shell remote code execution vulnerability (CVE-2025-55182)", https://www.zscaler.com/jp/blogs/security-research/react2shell-remote-code-execution-vulnerability-cve-2025-55182 (checked 2026-10-12 via search; the react.dev and nextjs.org advisories were not reachable from the review environment, so confirm the patched versions there before relying on them).

### Modern Code Audit Tools (2025)

| Tool | Purpose | Best For |
|------|---------|----------|
| **CodeQL** | Query-based analysis | GitHub-hosted projects |
| **Semgrep** | Pattern-based scanning | DevSecOps pipelines |
| **Snyk** | Dependency scanning | npm package vulnerabilities |
| **CodeAnt.ai** | AI-driven static analysis | Context-aware recommendations |
| **SonarQube** | Comprehensive code health | Technical debt metrics |

### Audit Workflow 2025

```bash
# 1. Security scan with CodeQL (TypeScript is analysed by the javascript extractor)
codeql database create --language=javascript --source-root=src db/
codeql database analyze db/ security-extended.qls --format=csv --output=results.csv

# 2. Dependency audit with Snyk
snyk test --severity-threshold=high

# 3. Semgrep pattern scanning
semgrep --config=auto --output=semgrep.json .

# 4. Generate combined report
# (scripts/audit-report.sh is not bundled with this skill; combine the outputs above manually)
```

<intake>
What type of audit would you like to perform?

1. **Security audit** - Scan for vulnerabilities, secrets, and security issues
2. **Code review** - Comprehensive code quality and architecture review
3. **Dependency audit** - Check dependencies for vulnerabilities and licensing
4. **Performance audit** - Identify bottlenecks and optimization opportunities
5. **Compliance audit** - Verify regulatory and licensing compliance

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "security", "vulnerability", "cve", "secrets" | `workflows/security-audit.md` |
| 2, "code", "review", "quality", "architecture" | `workflows/code-review.md` |
| 3, "dependency", "dependencies", "npm", "pip", "packages" | Not bundled with this skill: run the dependency scans above and read `references/best-practices.md` |
| 4, "performance", "perf", "bottleneck", "optimize" | Not bundled with this skill: use the code-review workflow and state the limitation |
| 5, "compliance", "license", "regulatory", "gdpr", "hipaa" | Not bundled with this skill: state that compliance review is out of scope for this bundle |

**After reading the workflow, follow it exactly.**
</routing>

<reference_index>
All domain knowledge in `references/`:

**Bundled**: `references/best-practices.md`

The following were listed in earlier versions and are **not bundled with this skill**: security-tools.md, vulnerability-detection.md, secrets-scanning.md, code-review-checklist.md, architecture-patterns.md, code-smells.md, dependency-management.md, license-compliance.md, performance-profiling.md, optimization-patterns.md, audit-reporting.md, risk-assessment.md.
</reference_index>

<workflows_index>
| Workflow | Purpose |
|----------|---------|
| security-audit.md | Scan for security vulnerabilities and secrets exposure |
| code-review.md | Comprehensive code quality and architecture assessment |
| dependency-audit.md | Not bundled with this skill |
| performance-audit.md | Not bundled with this skill |
| compliance-audit.md | Not bundled with this skill |
</workflows_index>

<success_criteria>
A comprehensive audit includes:
- All relevant scans executed (security, quality, dependencies)
- Issues categorized by severity and risk
- Actionable recommendations with examples
- Risk assessment for each finding
- Prioritized remediation plan
- Documentation of audit process and findings
- Executive summary for non-technical stakeholders
</success_criteria>
