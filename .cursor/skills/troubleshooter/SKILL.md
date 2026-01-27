---
name: troubleshooter
description: Diagnoses and resolves evaluation failures, patch application errors, and Salesforce issues. The agent invokes this skill when debugging problems, investigating errors, or troubleshooting failures.
---

# Troubleshooter

## Overview

This skill provides systematic troubleshooting methodology for SF-Bench issues. It covers evaluation failures, patch application errors, scratch org problems, and debugging strategies.

## When This Skill Applies

- Evaluation failures or unexpected errors
- Patch application issues
- Scratch org creation or deployment problems
- Debugging test failures
- Investigating root causes

## Troubleshooting Methodology

### Step 1: Categorize the Error

| Category | Indicators | Approach |
|----------|------------|----------|
| Tool Bug | Affects all tasks, reproducible | Fix in codebase |
| Model Limitation | Affects specific task types | Document, adjust prompts |
| Platform Constraint | Salesforce-specific errors | Work within limits |
| Configuration | Missing env vars, bad config | Fix configuration |
| Transient | Intermittent, network-related | Retry with backoff |

### Step 2: Gather Evidence

1. **Check Logs**
   ```bash
   # View recent logs
   ls -la logs/

   # Search for errors
   grep -r "ERROR" logs/

   # View specific task log
   cat logs/<run_id>/<model>/<task_id>.log
   ```

2. **Check Git Status**
   ```bash
   # Verify no manual tweaks
   git status

   # View applied patch
   git diff
   ```

3. **Check Scratch Org**
   ```bash
   # List orgs
   sf org list --all

   # View org details
   sf org display -o <alias>

   # Check deployment status
   sf project deploy report -o <alias>
   ```

### Step 3: Identify Root Cause

Use the error message to narrow down:

```
Error Message → Category → Root Cause → Fix
```

### Step 4: Apply Fix and Verify

1. Apply the fix
2. Run relevant tests
3. Verify the issue is resolved
4. Document if pattern-based

## Common Error Patterns

### Patch Application Failures

#### Error: "patch does not apply"
**Cause**: Patch context doesn't match file content

**Diagnosis**:
```bash
# Check file content
cat <file-path>

# Check patch preview
head -50 solution.patch
```

**Solutions**:
1. Verify correct repository version
2. Use fuzzy matching: `git apply --3way`
3. Regenerate solution with updated context

#### Error: "corrupt patch at line X"
**Cause**: Malformed patch format

**Diagnosis**:
```bash
# Validate patch syntax
git apply --check solution.patch
```

**Solutions**:
1. Check for markdown fences in patch
2. Remove standalone +/- lines
3. Verify patch header format

### Scratch Org Failures

#### Error: "SCRATCH_ORG_LIMIT_EXCEEDED"
**Cause**: Daily scratch org creation limit reached

**Diagnosis**:
```bash
# Check org limits
sf limits api display -o <devhub>
```

**Solutions**:
1. Delete unused scratch orgs
2. Wait for daily limit reset
3. Use different DevHub

#### Error: "InvalidOrgForCreate"
**Cause**: DevHub not authenticated or expired

**Diagnosis**:
```bash
# Check DevHub status
sf org list --all | grep DevHub
```

**Solutions**:
1. Re-authenticate: `sf org login web -d`
2. Verify DevHub features enabled
3. Check org expiration

### Deployment Failures

#### Error: "CANNOT_ENABLE_DEVELOPER_MODE"
**Cause**: Scratch org config issue

**Diagnosis**:
```bash
# Check scratch def
cat config/project-scratch-def.json
```

**Solutions**:
1. Verify features in scratch def
2. Check for conflicting settings
3. Use minimal scratch def

#### Error: "Test coverage is XX%, at least 75% required"
**Cause**: Insufficient test coverage

**Diagnosis**:
```bash
# Run tests with coverage
sf apex run test -o <alias> -c -r human
```

**Solutions**:
1. Add more test methods
2. Cover edge cases
3. Check for uncovered branches

### API Failures

#### Error: "rate_limit_exceeded"
**Cause**: AI provider rate limit

**Diagnosis**:
- Check request frequency
- Review provider dashboard

**Solutions**:
1. Implement rate limiting
2. Use exponential backoff
3. Switch to different provider

#### Error: "invalid_api_key"
**Cause**: Missing or incorrect API key

**Diagnosis**:
```bash
# Check environment
echo $ROUTELLM_API_KEY | head -c 10
```

**Solutions**:
1. Verify key in .env
2. Source environment: `source .env`
3. Regenerate API key

## Diagnostic Commands

### Preflight Diagnostics
```bash
# Run preflight checks
python -c "
from sfbench.utils.preflight import PreflightValidator
v = PreflightValidator()
r = v.run_all_checks('model-name', 'provider')
print('PASSED' if r.passed else 'FAILED')
for c in r.checks:
    print(f'{c.name}: {c.status}')
"
```

### Scratch Org Diagnostics
```bash
# Create debug org
sf org create scratch -f config/project-scratch-def.json -a debug-org -d 1

# Deploy and check
sf project deploy start -o debug-org

# Run specific test
sf apex run test -o debug-org -n TestClassName -r human -c

# Cleanup
sf org delete scratch -o debug-org -p
```

### Patch Diagnostics
```bash
# Validate patch
git apply --check solution.patch

# Apply with verbose output
git apply -v solution.patch

# Apply with fallback strategies
git apply --3way solution.patch
git apply --reject solution.patch
```

## Escalation Path

If issue persists after troubleshooting:

1. **Document the Issue**
   - Error message
   - Steps to reproduce
   - Environment details
   - Attempted solutions

2. **Update activeContext.md**
   - Add to "Blockers" section
   - Note impact on current work

3. **Create Issue**
   - Use bug report template
   - Include all diagnostic information
   - Tag appropriately

## Prevention Strategies

### For Patch Issues
- Validate patches before applying
- Use multi-strategy fallback
- Clean patches before application

### For Scratch Org Issues
- Monitor org limits
- Always cleanup in finally blocks
- Use retry with exponential backoff

### For API Issues
- Implement rate limiting
- Cache responses where appropriate
- Use circuit breaker pattern for repeated failures
