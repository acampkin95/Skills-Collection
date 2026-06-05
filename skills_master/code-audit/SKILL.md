---
name: code-audit
description: Comprehensive security audits, vulnerability scanning, and code quality assessment.
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

### Next.js RCE Vulnerabilities (CVE-2025)

Two critical Remote Code Execution vulnerabilities affect React Server Components:

| CVE | Severity | Description | Affected Versions |
|-----|----------|-------------|-------------------|
| CVE-2025-55182 | Critical | RSC vulnerability | Next.js < 16.0.10 |
| CVE-2025-66478 | Critical | RCE with working exploit | Next.js < 16.0.10 |

**IMMEDIATE ACTION REQUIRED:**
- Upgrade to Next.js 16.0.10+ if using App Router with React Server Components
- If upgrade not possible, implement WAF rules blocking malicious requests

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
# 1. Security scan with CodeQL
codeql database create --language=typescript --source-root=src db/
codeql database analyze db/ security-extended.qls --format=csv --output=results.csv

# 2. Dependency audit with Snyk
snyk test --severity-threshold=high

# 3. Semgrep pattern scanning
semgrep --config=auto --output=semgrep.json .

# 4. Generate combined report
./scripts/audit-report.sh --format=markdown
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
| 3, "dependency", "dependencies", "npm", "pip", "packages" | `workflows/dependency-audit.md` |
| 4, "performance", "perf", "bottleneck", "optimize" | `workflows/performance-audit.md` |
| 5, "compliance", "license", "regulatory", "gdpr", "hipaa" | `workflows/compliance-audit.md` |

**After reading the workflow, follow it exactly.**
</routing>

<reference_index>
All domain knowledge in `references/`:

**Security**: security-tools.md, vulnerability-detection.md, secrets-scanning.md
**Code Quality**: code-review-checklist.md, architecture-patterns.md, code-smells.md
**Dependencies**: dependency-management.md, license-compliance.md
**Performance**: performance-profiling.md, optimization-patterns.md
**Reporting**: audit-reporting.md, risk-assessment.md
</reference_index>

<workflows_index>
| Workflow | Purpose |
|----------|---------|
| security-audit.md | Scan for security vulnerabilities and secrets exposure |
| code-review.md | Comprehensive code quality and architecture assessment |
| dependency-audit.md | Check dependencies for vulnerabilities and licenses |
| performance-audit.md | Identify performance bottlenecks and opportunities |
| compliance-audit.md | Verify regulatory and licensing compliance |
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
