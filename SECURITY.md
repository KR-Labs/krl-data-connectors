# Security Policy

## KRL Defense & Protection Stack

This project implements a comprehensive 10-layer security architecture designed to protect intellectual property, prevent vulnerabilities, and ensure secure development practices.

## Reporting Security Vulnerabilities

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@kr-labs.org**

Include the following information:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability

We will acknowledge receipt within 48 hours and provide a more detailed response within 5 business days.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Measures

### Layer 1: Legal Protection

**Status:** ACTIVE (Implemented Oct 2025)

All source code files include:
- Copyright headers: `© 2025 KR-Labs. All rights reserved.`
- Trademark notices: `KR-Labs™ is a trademark of Quipu Research Labs, LLC`
- License identifiers: `SPDX-License-Identifier: Apache-2.0`

**Coverage:** 198/198 files (100%)

**Verification:**
```bash
python scripts/security/verify_copyright_headers.py
```

### Layer 2: Technical Protection (Secret Scanning)

**Status:** ACTIVE (Implemented Oct 2025)

Multi-layered secret detection:

1. **GitHub Secret Scanning** (Push Protection)
   - Automatically scans all commits pushed to GitHub
   - Blocks pushes containing detected secrets
   - Covers 200+ secret patterns

2. **Gitleaks** (Local & CI/CD)
   - Version: 8.28.0
   - Pre-commit hook prevents local commits with secrets
   - CI/CD integration scans every PR
   - Configuration: `.gitleaks.toml`

3. **Historical Validation**
   - Full repository history scanned: 145 commits, 5.42 MB
   - Result: ✅ Zero secrets detected

**Usage:**
```bash
# Run local scan
gitleaks detect --config .gitleaks.toml --verbose

# Check specific files
gitleaks detect --config .gitleaks.toml --no-git --source path/to/file.py
```

### Layer 3: Code Signing & Watermarking

**Status:** PLANNED (Week 7)

- GPG signing for all releases
- Build watermarking for provenance tracking
- PyPI trusted publisher authentication

### Layer 4: Runtime Protection

**Status:** NOT APPLICABLE

Data connectors do not have runtime protection requirements as they are libraries, not services.

### Layer 5: Build Verification

**Status:** ACTIVE (CI/CD Security)

Automated security checks on every commit:

- **Copyright & Trademark Verification**
- **Secret Scanning** (Gitleaks)
- **Vulnerability Scanning** (Trivy)
- **Python Security Checks** (Bandit, Safety)
- **CodeQL Analysis** (Security-extended queries)
- **Dependency Review** (On pull requests)
- **License Compliance** (Licensee)

**GitHub Actions:** `.github/workflows/security-checks.yml`

### Layer 6: License Enforcement

**Status:** ACTIVE

- Primary license: Apache 2.0
- All dependencies verified for compatibility
- GPL licenses explicitly blocked
- License scanning in CI/CD pipeline

### Layer 7: Distribution Control

**Status:** ACTIVE

- PyPI package signing (upcoming)
- GitHub Releases only
- Verified publisher status
- No unofficial distribution channels

### Layer 8: Contributor Agreement (CLA)

**Status:** DOCUMENTED

Contributors must agree to:
- Assign copyright to KR-Labs
- Accept Apache 2.0 license terms
- Follow security guidelines

See `CONTRIBUTING.md` for details.

### Layer 9: CI/CD Security

**Status:** ACTIVE

All changes undergo:
- Automated security scanning
- Secret detection
- Vulnerability checks
- License compliance verification
- Code quality analysis

### Layer 10: Monitoring & Response

**Status:** ACTIVE

- GitHub Security Advisories enabled
- Dependabot alerts enabled
- Security tab monitoring
- Automated vulnerability notifications

## Security Best Practices for Contributors

### Before Committing

1. **Never commit secrets or credentials**
   - Use environment variables
   - Use `.env` files (excluded from git)
   - Pre-commit hooks will block most secrets

2. **Review changes carefully**
   ```bash
   git diff --staged
   ```

3. **Run security checks locally**
   ```bash
   pre-commit run --all-files
   gitleaks detect --config .gitleaks.toml --verbose
   ```

### API Keys & Credentials

**Never include in code:**
- API keys
- Passwords
- Tokens
- Private keys
- Connection strings

**Use instead:**
- Environment variables: `os.environ.get('API_KEY')`
- Configuration files (gitignored)
- Secret management services (AWS Secrets Manager, etc.)

### Testing with Real Data

When testing connectors:
1. Use official demo/test API keys when available
2. Store personal keys in `.env` file (gitignored)
3. Use placeholder values in documentation
4. Never commit real API responses containing sensitive data

### Code Review Checklist

Before approving PRs, verify:
- [ ] No secrets in code or commits
- [ ] Copyright headers present
- [ ] No hardcoded credentials
- [ ] No GPL-licensed dependencies
- [ ] Security checks pass
- [ ] No sensitive data in test files

## Vulnerability Disclosure Timeline

1. **Initial Report:** Acknowledgment within 48 hours
2. **Triage:** Assessment within 5 business days
3. **Fix Development:** Timeline communicated to reporter
4. **Fix Testing:** Internal validation
5. **Release:** Coordinated disclosure
6. **Public Disclosure:** After fix is released

## Security Update Process

When a security vulnerability is fixed:

1. **Private Fix:** Develop patch in private repository
2. **Security Advisory:** Create GitHub Security Advisory
3. **CVE Assignment:** Request CVE if applicable
4. **Release:** Publish patched version
5. **Notification:** Email security@kr-labs.org subscribers
6. **Public Disclosure:** Update SECURITY.md and GitHub Advisory

## Dependency Security

We use multiple tools to ensure dependency security:

- **Dependabot:** Automated dependency updates
- **Safety:** Python package vulnerability scanning
- **Trivy:** Comprehensive vulnerability scanning
- **Dependency Review:** GitHub's built-in review action

### Checking Dependencies

```bash
# Check for known vulnerabilities
safety check

# Scan with Trivy
trivy fs .

# Review dependency tree
pip list --outdated
```

## Incident Response

If a security incident is detected:

1. **Immediate:** Notify security@kr-labs.org
2. **Assessment:** Determine scope and impact
3. **Containment:** Disable affected systems if needed
4. **Remediation:** Deploy fix
5. **Post-Mortem:** Document lessons learned
6. **Communication:** Notify affected users

## Security Contacts

- **Email:** security@kr-labs.org
- **PGP Key:** Available on request
- **GitHub:** Open security advisory (for non-critical issues)

## Acknowledgments

We appreciate responsible disclosure of security vulnerabilities. Contributors who report valid security issues may be acknowledged in our release notes (with permission).

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

Last Updated: October 22, 2025
