---
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
---

# Security Compliance Quick Action Checklist

**Repository**: krl-data-connectors  
**Date**: October 22, 2025  
**Current Compliance**: 9.6% (5/52 files)  
**Target Compliance**: 100% (52/52 files)  

---

## 🔴 URGENT: Phase 1 - Legal Protection (Do Today)

### Task 1: Copyright Header Injection ⏱️ 1 hour

**Status**: ⬜ Not Started  
**Priority**: 🔴 CRITICAL  
**Impact**: Brings 47 files to compliance  

```bash
# Step 1: Navigate to repository
cd /Users/bcdelo/KR-Labs/krl-data-connectors

# Step 2: Test script (dry run - see what it would do)
python /Users/bcdelo/KR-Labs/scripts/security/add_copyright_headers.py --dry-run

# Step 3: Review dry run output
# Check that it's targeting the right files

# Step 4: Apply copyright headers
python /Users/bcdelo/KR-Labs/scripts/security/add_copyright_headers.py

# Step 5: Verify compliance
python /Users/bcdelo/KR-Labs/scripts/security/verify_copyright_headers.py

# Expected output:
# ✓ Copyright header injection complete!
# Total files scanned:     52
# Files modified:          47
# Files already compliant: 5
# Files with errors:       0
```

**Checklist**:
- [ ] Dry run completed successfully
- [ ] Output reviewed and looks correct
- [ ] Script executed on all files
- [ ] Verification script shows 52/52 compliant
- [ ] Git diff reviewed
- [ ] No unintended changes made

**Success Criteria**:
- ✅ All 52 connector files have copyright headers
- ✅ All 52 files have KRL™ trademark notices
- ✅ All 52 files have Apache 2.0 SPDX license
- ✅ No code functionality changed

---

### Task 2: Commit Legal Protection Changes ⏱️ 10 minutes

**Status**: ⬜ Not Started  
**Depends On**: Task 1 completed  

```bash
# Review changes
git status
git diff

# Stage all changes
git add src/krl_data_connectors

# Commit with descriptive message
git commit -m "feat(security): Add copyright headers and trademark notices to all connectors

- Added copyright headers to 47 connector files
- Added KRL™ trademark notices
- Added Apache 2.0 SPDX license identifiers
- Brings repository to 100% legal compliance
- Ref: SECURITY_AUDIT_REPORT.md"

# Push to remote
git push origin main
```

**Checklist**:
- [ ] Changes reviewed in git diff
- [ ] Commit message is descriptive
- [ ] Pushed to main branch successfully
- [ ] GitHub shows updated files

---

## 🔴 URGENT: Phase 2 - Secret Scanning Setup (Do Today)

### Task 3: Install Gitleaks ⏱️ 5 minutes

**Status**: ⬜ Not Started  
**Priority**: 🔴 HIGH  

```bash
# macOS installation
brew install gitleaks

# Verify installation
gitleaks version

# Expected output: 8.x.x or higher
```

**Checklist**:
- [ ] Gitleaks installed successfully
- [ ] Version command works

---

### Task 4: Configure Gitleaks ⏱️ 10 minutes

**Status**: ⬜ Not Started  
**Depends On**: Task 3 completed  

```bash
cd /Users/bcdelo/KR-Labs/krl-data-connectors

# Copy Gitleaks configuration
cp /Users/bcdelo/KR-Labs/.gitleaks.toml .

# Verify configuration exists
cat .gitleaks.toml | head -20

# Add to git
git add .gitleaks.toml
git commit -m "ci: Add Gitleaks secret scanning configuration"
git push origin main
```

**Checklist**:
- [ ] .gitleaks.toml copied to repository
- [ ] Configuration reviewed
- [ ] Committed to repository

---

### Task 5: Run Historical Secret Scan ⏱️ 5 minutes

**Status**: ⬜ Not Started  
**Depends On**: Task 4 completed  

```bash
cd /Users/bcdelo/KR-Labs/krl-data-connectors

# Scan entire repository history
gitleaks detect --config .gitleaks.toml --verbose

# If secrets found:
# 1. Review findings
# 2. Determine if false positives
# 3. Rotate any real secrets immediately
# 4. Use git-filter-repo to remove from history if needed

# Expected output (based on audit):
# ✓ No leaks detected
```

**Checklist**:
- [ ] Historical scan completed
- [ ] Results reviewed
- [ ] No real secrets detected (✅ per audit)
- [ ] Any false positives documented

---

### Task 6: Install Pre-Commit Hooks ⏱️ 10 minutes

**Status**: ⬜ Not Started  
**Depends On**: Task 4 completed  

```bash
cd /Users/bcdelo/KR-Labs/krl-data-connectors

# Install pre-commit
pip install pre-commit

# Copy configuration (if not already present)
if [ ! -f .pre-commit-config.yaml ]; then
  cp /Users/bcdelo/KR-Labs/.pre-commit-config.yaml .
fi

# Install hooks
pre-commit install

# Test hooks on all files
pre-commit run --all-files

# Expected: All checks should pass
```

**Checklist**:
- [ ] pre-commit installed
- [ ] .pre-commit-config.yaml in place
- [ ] Hooks installed successfully
- [ ] Test run passes all checks

---

### Task 7: Test Secret Prevention ⏱️ 5 minutes

**Status**: ⬜ Not Started  
**Depends On**: Task 6 completed  

```bash
cd /Users/bcdelo/KR-Labs/krl-data-connectors

# Create a test file with a fake secret
echo 'API_KEY = "sk_test_FAKE_KEY_FOR_TESTING"' > test_secret.py

# Try to commit (should be BLOCKED)
git add test_secret.py
git commit -m "test"

# Expected output:
# ✗ Secret detected! Commit blocked.

# Clean up
rm test_secret.py
git reset HEAD

# Success! Secrets are now prevented.
```

**Checklist**:
- [ ] Test secret file created
- [ ] Commit was blocked by pre-commit hook
- [ ] Error message displayed
- [ ] Test file cleaned up
- [ ] Secret prevention confirmed working

---

## 🟡 HIGH PRIORITY: Phase 3 - CI/CD Security (This Week)

### Task 8: Create GitHub Actions Workflow ⏱️ 30 minutes

**Status**: ⬜ Not Started  
**Priority**: 🟡 HIGH  

```bash
cd /Users/bcdelo/KR-Labs/krl-data-connectors

# Create workflows directory
mkdir -p .github/workflows

# Copy security workflow
cp /Users/bcdelo/KR-Labs/.github/workflows/security-checks.yml .github/workflows/

# Review workflow
cat .github/workflows/security-checks.yml

# Commit
git add .github/workflows/security-checks.yml
git commit -m "ci: Add automated security scanning workflow

- Runs Gitleaks on every PR
- Verifies copyright headers
- Enforces trademark compliance
- Prevents secret leaks"
git push origin main
```

**Checklist**:
- [ ] Workflow file copied
- [ ] Workflow reviewed and understood
- [ ] Committed to repository
- [ ] GitHub Actions enabled on repository

---

### Task 9: Test GitHub Actions Workflow ⏱️ 15 minutes

**Status**: ⬜ Not Started  
**Depends On**: Task 8 completed  

```bash
# Method 1: Create a test PR
git checkout -b test/security-workflow
echo "# Test" >> README.md
git add README.md
git commit -m "test: Trigger security workflow"
git push origin test/security-workflow

# Create PR on GitHub
# Watch Actions tab for workflow execution

# Method 2: Manual workflow trigger
# GitHub.com → Actions → security-checks → Run workflow

# Expected: All checks pass ✅
```

**Checklist**:
- [ ] Test PR created
- [ ] Workflow triggered automatically
- [ ] All security checks passed
- [ ] Workflow logs reviewed
- [ ] Test PR closed/deleted

---

### Task 10: Document Security Practices ⏱️ 1 hour

**Status**: ⬜ Not Started  
**Priority**: 🟡 MEDIUM  

Create or update these files:

**SECURITY.md**:
```markdown
# Security Policy

## Reporting Security Issues

Please report security vulnerabilities to: security@krlabs.dev

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Measures

- Automated secret scanning (Gitleaks)
- Pre-commit hooks prevent secret commits
- Copyright and trademark protection
- Apache 2.0 open source license
```

**Update CONTRIBUTING.md**:
Add security section:
```markdown
## Security Guidelines

1. Never commit API keys or secrets
2. Use environment variables for credentials
3. Run `pre-commit` hooks before pushing
4. Report security issues privately to security@krlabs.dev
```

**Checklist**:
- [ ] SECURITY.md created
- [ ] CONTRIBUTING.md updated
- [ ] README.md updated (if needed)
- [ ] Files committed and pushed

---

## 🟢 MEDIUM PRIORITY: Phase 4 - Advanced Protection (Next 2 Weeks)

### Task 11: Code Signing Setup (Week 7 in Guide)

**Status**: ⬜ Not Started  
**Priority**: 🟢 MEDIUM  
**Timeline**: Follow Week 7 in KRL_DEFENSE_IMPLEMENTATION_GUIDE.md  

**Prerequisites**:
- GPG key generated
- GitHub secrets configured
- PyPI trusted publisher setup

**Estimated Time**: 4 hours

---

### Task 12: Build Watermarking (Week 7 in Guide)

**Status**: ⬜ Not Started  
**Priority**: 🟢 MEDIUM  
**Timeline**: Follow Week 7 in KRL_DEFENSE_IMPLEMENTATION_GUIDE.md  

**Prerequisites**:
- Code signing complete
- Build workflow configured

**Estimated Time**: 2 hours

---

## Progress Tracker

### Overall Progress
```
Phase 1 (Legal):      [░░░░░░░░░░░░░░░░░░░░] 0/2 tasks (0%)
Phase 2 (Secrets):    [░░░░░░░░░░░░░░░░░░░░] 0/5 tasks (0%)
Phase 3 (CI/CD):      [░░░░░░░░░░░░░░░░░░░░] 0/3 tasks (0%)
Phase 4 (Advanced):   [░░░░░░░░░░░░░░░░░░░░] 0/2 tasks (0%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total:                [░░░░░░░░░░░░░░░░░░░░] 0/12 tasks (0%)
```

### Time Investment
- **Phase 1**: ~1.5 hours (URGENT - Do Today)
- **Phase 2**: ~35 minutes (URGENT - Do Today)
- **Phase 3**: ~1.75 hours (This Week)
- **Phase 4**: ~6 hours (Next 2 Weeks)
- **Total**: ~9.5 hours to full compliance

### Expected Outcomes by Phase

**After Phase 1**:
- ✅ 52/52 files legally compliant
- ✅ Copyright, trademark, license headers on all files
- ✅ No legal vulnerabilities

**After Phase 2**:
- ✅ Automated secret scanning active
- ✅ Pre-commit hooks prevent future leaks
- ✅ Historical scan confirms no past leaks
- ✅ Team protected from accidental secret commits

**After Phase 3**:
- ✅ CI/CD enforces security on every PR
- ✅ Automated compliance checking
- ✅ Security documentation complete
- ✅ Team educated on practices

**After Phase 4**:
- ✅ Package releases are signed and verifiable
- ✅ Build provenance tracked with watermarks
- ✅ Full 10-layer defense stack active
- ✅ Industry-leading security posture

---

## Quick Start Guide

### Today's Priority (2 hours total)

1. **Run copyright script** (1 hour)
   - Brings 47 files to compliance
   - Zero risk, high reward
   
2. **Set up secret scanning** (30 mins)
   - Prevents future security issues
   - One-time setup

3. **Test and verify** (30 mins)
   - Confirm everything works
   - Document completion

### This Week (2 hours)

4. **Set up GitHub Actions** (2 hours)
   - Automate security checks
   - Enforce on all PRs

### Next 2 Weeks (6 hours)

5. **Implement code signing** (4 hours)
6. **Add build watermarking** (2 hours)

---

## Success Metrics

### Current State
- Legal Compliance: 9.6% (5/52 files)
- Secret Protection: Manual only
- Automated Checks: None
- Documentation: Minimal

### Target State (After All Phases)
- Legal Compliance: 100% (52/52 files) ✅
- Secret Protection: Automated prevention ✅
- Automated Checks: CI/CD enforced ✅
- Documentation: Complete ✅

---

## Notes & Updates

**[DATE] - [TIME]**: 
- Task completed: 
- Issues encountered: 
- Resolution: 

---

**Ready to start?** Begin with Task 1: Copyright Header Injection

**Questions?** Refer to:
- SECURITY_AUDIT_REPORT.md (detailed analysis)
- KRL_DEFENSE_IMPLEMENTATION_GUIDE.md (full guide)

**Status**: ⬜ Not Started | In Progress: 0/12 tasks
