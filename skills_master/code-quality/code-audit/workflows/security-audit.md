# Security Audit Workflow

<required_reading>
Before starting, read:
- `references/security-tools.md` — Available security scanning tools and configurations
- `references/vulnerability-detection.md` — Common vulnerability patterns and detection methods
- `references/secrets-scanning.md` — Secrets detection and prevention strategies
</required_reading>

<process>
## Phase 1: Automated Security Scanning

### Step 1: Dependency Vulnerability Scanning
**Tools to use:**
- **npm**: `npm audit` for Node.js projects
- **pip**: `safety check` or `pip-audit` for Python projects
- **bundler**: `bundle audit` for Ruby projects
- **Snyk**: Cross-platform vulnerability scanning

**Process:**
1. Run dependency vulnerability scan
2. Generate vulnerability report with severity levels
3. Identify direct vs. transitive dependencies
4. Check for available security patches
5. Document findings with CVE numbers and CVSS scores

### Step 2: Secrets and Credentials Scanning
**Tools to use:**
- **truffleHog**: Git history scanning for secrets
- **git-secrets**: AWS credential detection
- **detect-secrets**: Multi-platform secret detection
- **gitleaks**: Comprehensive secret scanning

**Common Secret Patterns:**
- API keys and tokens
- Database connection strings
- Private SSH keys
- OAuth tokens and client secrets
- Environment configuration with credentials

**Process:**
1. Scan entire git history for exposed secrets
2. Check configuration files and environment variables
3. Identify hardcoded credentials in source code
4. Document all findings with severity assessment
5. Provide remediation steps for each finding

### Step 3: Static Application Security Testing (SAST)
**Tools to use:**
- **Bandit**: Python security linting
- **ESLint Security**: JavaScript security rules
- **Brakeman**: Rails security scanning
- **CodeQL**: GitHub's semantic code analysis
- **SonarQube**: Multi-language security analysis

**Security Patterns to Check:**
- SQL injection vulnerabilities
- Cross-site scripting (XSS) potential
- Command injection risks
- Path traversal vulnerabilities
- Insecure cryptographic practices
- Authentication and authorization flaws

## Phase 2: Manual Security Review

### Step 1: Authentication & Authorization Analysis
**Review Areas:**
- Authentication mechanisms (JWT, sessions, OAuth)
- Password policies and storage (bcrypt, scrypt, Argon2)
- Multi-factor authentication implementation
- Session management and timeout policies
- Permission and role-based access controls
- API authentication and rate limiting

**Security Checklist:**
- ✅ Passwords are properly hashed with salt
- ✅ Sessions are securely managed and expire appropriately
- ✅ Authentication failures are handled securely
- ✅ Authorization checks are consistently applied
- ✅ Sensitive operations require re-authentication
- ✅ API endpoints have proper access controls

### Step 2: Input Validation & Output Encoding
**Review Areas:**
- User input validation and sanitization
- SQL query parameterization
- HTML output encoding
- File upload restrictions
- API input validation
- Error message information disclosure

**Security Checklist:**
- ✅ All user inputs are validated and sanitized
- ✅ SQL queries use parameterized statements
- ✅ HTML outputs are properly encoded
- ✅ File uploads are restricted and validated
- ✅ Error messages don't reveal sensitive information
- ✅ CSRF protection is implemented where needed

### Step 3: Data Protection & Privacy
**Review Areas:**
- Data encryption at rest and in transit
- Personal data handling and GDPR compliance
- Sensitive data logging practices
- Backup security and access controls
- Third-party data sharing agreements
- Data retention and deletion policies

**Security Checklist:**
- ✅ Sensitive data is encrypted using strong algorithms
- ✅ TLS/SSL is properly configured and enforced
- ✅ Personal data is handled according to privacy laws
- ✅ Sensitive information is not logged
- ✅ Backups are secured and encrypted
- ✅ Data retention policies are implemented

## Phase 3: Infrastructure & Configuration Review

### Step 1: Server & Network Security
**Review Areas:**
- Server hardening and configuration
- Network segmentation and firewall rules
- Load balancer and reverse proxy configuration
- Container security (if applicable)
- Cloud security configuration (AWS, GCP, Azure)
- Monitoring and logging setup

### Step 2: Third-Party Dependencies
**Review Areas:**
- Dependency update policies
- Third-party service integrations
- External API security
- Library and framework security practices
- Supply chain security considerations

## Phase 4: Risk Assessment & Reporting

### Step 1: Vulnerability Prioritization
**Risk Matrix:**
- **Critical**: Immediate exploitation possible, high business impact
- **High**: Likely exploitation, significant impact
- **Medium**: Possible exploitation, moderate impact
- **Low**: Difficult exploitation, minimal impact

**Factors to Consider:**
- Exploitability (how easy to exploit)
- Business impact (data, reputation, financial)
- Attack surface (public-facing vs. internal)
- Existing mitigations and controls

### Step 2: Security Report Generation
**Report Structure:**
1. **Executive Summary**
   - Overall security posture assessment
   - Critical findings requiring immediate attention
   - Risk rating and business impact

2. **Detailed Findings**
   - Vulnerability descriptions and evidence
   - Risk ratings with justification
   - Specific remediation recommendations
   - Timeline for fixes (immediate, short-term, long-term)

3. **Remediation Plan**
   - Prioritized action items
   - Resource requirements
   - Implementation timeline
   - Validation and testing requirements

### Step 3: Remediation Tracking
**Follow-up Process:**
- Create tickets for each security finding
- Assign owners and due dates
- Regular progress reviews
- Re-testing after fixes
- Security metrics and improvement tracking
</process>

<success_criteria>
Security audit is complete when:
- All automated security scans have been executed
- Manual security review has been conducted across all critical areas
- All findings have been documented with risk ratings
- Remediation plan has been created with prioritized actions
- Report has been delivered to stakeholders
- Critical vulnerabilities have immediate remediation timeline
- Security improvement recommendations are actionable
- Follow-up process is established for tracking fixes
</success_criteria>