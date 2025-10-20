# Branch Protection Setup Guide

This guide explains how to set up branch protection for the `main` branch using GitHub Rulesets.

## Quick Summary

Two ruleset files are provided:

1. **`branch-protection-ruleset.json`** - Full protection (includes CI checks)
2. **`branch-protection-ruleset-simple.json`** - Minimal protection (no CI checks)

## What These Rulesets Do

### Both Rulesets Include:
- ✅ **Block branch deletion** - Cannot delete `main` branch
- ✅ **Block force pushes** - Cannot `git push --force` to `main`
- ⚠️ **Bypass permissions** - You'll need to add "Repository admin" bypass manually after import

### Full Ruleset Additionally Includes:
- ✅ **Require CI checks to pass** - Tests and Lint workflows must succeed
- ✅ **Require branches up-to-date** - Must merge latest `main` before merging PR

## Option 1: Upload via GitHub UI (Recommended)

### Step 1: Navigate to Rulesets
1. Go to: https://github.com/KR-Labs/krl-data-connectors/settings/rules
2. Click: **"New ruleset"** → **"Import a ruleset"**

### Step 2: Upload JSON File
1. Click **"Choose file"** or drag and drop
2. Select: `branch-protection-ruleset-simple.json` (start with minimal)
3. Click **"Import"**

### Step 3: Configure Bypass Permissions (IMPORTANT!)
After importing, you'll see the ruleset configuration:

1. Scroll to **"Bypass list"** section
2. Click **"Add bypass"**
3. Select **"Repository admin"** from the dropdown
4. Set bypass mode to **"Always"**
5. This ensures YOU can bypass rules in emergencies!

### Step 4: Save and Activate
1. Review all settings
2. Click **"Create"** at the bottom
3. Ruleset is now active!

### Step 5: Verify
The ruleset should now be active. You can view it at:
https://github.com/KR-Labs/krl-data-connectors/settings/rules

## Option 2: Apply via GitHub CLI

### Using Simple Ruleset (Recommended First):
```bash
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/KR-Labs/krl-data-connectors/rulesets \
  --input branch-protection-ruleset-simple.json
```

### Using Full Ruleset (After CI Workflows Configured):
```bash
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/KR-Labs/krl-data-connectors/rulesets \
  --input branch-protection-ruleset.json
```

## Testing the Protection

### Test 1: Try Force Push (Should Fail)
```bash
# This should be blocked:
git push --force origin main
```

**Expected output:**
```
remote: error: GH013: Repository rule violations found for refs/heads/main.
```

### Test 2: Normal Push (Should Work)
```bash
# This should work:
git push origin main
```

### Test 3: Try to Delete Branch (Should Fail)
```bash
# This should be blocked:
git push origin --delete main
```

## Bypass in Emergencies

As a repository administrator, you can bypass these rules when needed:

1. Go to: https://github.com/KR-Labs/krl-data-connectors/settings/rules
2. Find your ruleset
3. Click **"Edit"**
4. Temporarily disable by changing enforcement to **"Disabled"**
5. Make your emergency changes
6. Re-enable by changing enforcement back to **"Active"**

**OR** use the `--force-with-lease` option (safer than `--force`):
```bash
git push --force-with-lease origin main
```

## Upgrading from Simple to Full

Once you've confirmed CI workflows are working:

1. Delete the simple ruleset
2. Upload/apply the full ruleset with CI checks
3. This adds automatic test validation before merging

## What Gets Protected

### ✅ Prevents:
- Accidental `git push --force` (loses history)
- Accidental branch deletion
- Merging code with failing tests (full ruleset only)

### ✅ Allows:
- Normal git workflow
- Admin bypass for emergencies
- All feature branch operations

### ✅ Benefits:
- Professional repository governance
- Protection from mistakes
- Ready for future collaborators
- Institutional credibility

## Troubleshooting

### Issue: "Actor base role does not have write permissions" or "invalid actor"
**Solution:** 
- Remove the `bypass_actors` section from the JSON (already done in these files)
- Add bypass permissions manually in the GitHub UI after import
- Go to the imported ruleset → Edit → Bypass list → Add "Repository admin"

### Issue: Status checks failing
**Solution:** 
1. Use the simple ruleset first (no CI requirements)
2. Verify your CI workflows are running
3. Check workflow names match: "Tests" and "Lint"
4. Upgrade to full ruleset once CI is stable

### Issue: Can't push to main
**Solution:** This is working as intended! Two options:
1. Work on a feature branch and create a PR
2. Temporarily disable the ruleset for emergency changes

## Files in This Directory

- `branch-protection-ruleset.json` - Full protection with CI checks
- `branch-protection-ruleset-simple.json` - Minimal protection only
- `BRANCH_PROTECTION_SETUP.md` - This file

## Additional Resources

- [GitHub Rulesets Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Available Ruleset Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)

## Recommendation

**Start with:** `branch-protection-ruleset-simple.json`
- Minimal friction
- Core protections active
- Easy to verify working

**Upgrade to:** `branch-protection-ruleset.json`
- After CI workflows are stable
- When you want enforced test passing
- Before adding collaborators

---

*Last updated: October 20, 2025*
