---
name: code-reviewer
description: Performs code reviews following SF-Bench quality standards. The agent invokes this skill when reviewing code, evaluating pull requests, or assessing code quality for production-readiness.
---

# Code Reviewer

## Overview

This skill provides a structured code review process following SF-Bench quality standards. It focuses on production-readiness, error handling, and adherence to project conventions.

## When This Skill Applies

- Reviewing code changes or pull requests
- Assessing code quality before merging
- Evaluating production-readiness
- Checking adherence to project standards

## Review Checklist

### Critical (Must Fix)

#### Error Handling
- [ ] Retry logic for transient operations (API calls, org creation)
- [ ] Exponential backoff implemented correctly (2^n pattern)
- [ ] Errors logged with full context (task ID, attempt number, error details)
- [ ] No silent failures (all exceptions handled or propagated)

#### Resource Management
- [ ] Scratch orgs deleted in finally blocks
- [ ] Context managers used for file/connection handling
- [ ] No resource leaks (unclosed connections, orphaned processes)
- [ ] Timeouts set for external operations

#### Security
- [ ] No hardcoded secrets or credentials
- [ ] API keys read from environment variables
- [ ] Sensitive data not logged
- [ ] Input validation for user-provided data

### Important (Should Fix)

#### Code Quality
- [ ] PEP 8 compliance (line length 100)
- [ ] Type hints on all function signatures
- [ ] Docstrings follow Google style format
- [ ] Functions focused and small (< 50 lines)

#### Logging
- [ ] Structured logging with appropriate levels
- [ ] Context included (task ID, operation name)
- [ ] Debug logs for troubleshooting
- [ ] No excessive logging in hot paths

#### Testing
- [ ] Unit tests for new functionality
- [ ] Edge cases covered
- [ ] Error conditions tested
- [ ] Test coverage meets threshold (≥80%)

### Suggestions (Nice to Have)

#### Performance
- [ ] Parallel processing where safe
- [ ] Caching for expensive operations
- [ ] Batch API calls when possible
- [ ] No unnecessary iterations

#### Documentation
- [ ] Complex logic explained in comments
- [ ] README updated if needed
- [ ] Docstrings accurate and complete
- [ ] Examples provided for non-obvious usage

## Review Process

### Step 1: Understand the Change
1. Read the PR description or commit message
2. Identify the scope (files changed, components affected)
3. Understand the intended behavior

### Step 2: Check Critical Issues
1. Scan for error handling patterns
2. Verify resource cleanup
3. Check for security issues
4. Identify any breaking changes

### Step 3: Review Code Quality
1. Check adherence to style guidelines
2. Verify type hints and docstrings
3. Assess test coverage
4. Review logging practices

### Step 4: Validate Functionality
1. Trace the code path mentally
2. Identify edge cases
3. Check error scenarios
4. Verify business logic correctness

### Step 5: Provide Feedback
1. Prioritize issues (Critical > Important > Suggestions)
2. Provide specific line references
3. Suggest alternatives when rejecting
4. Acknowledge good patterns

## Feedback Format

### For Issues
```
**[CRITICAL/IMPORTANT/SUGGESTION]** Line XX-YY

**Issue**: [Brief description of the problem]

**Why**: [Explanation of why this is problematic]

**Suggestion**: [Recommended fix or alternative]
```

### For Approval
```
**Approved**

Changes look good. Key observations:
- [Positive observation 1]
- [Positive observation 2]

Minor suggestions (non-blocking):
- [Optional improvement 1]
```

## SF-Bench Specific Patterns

### Retry Pattern (Required for transient operations)
```python
# Expected pattern
for attempt in range(max_retries):
    try:
        result = operation()
        return result
    except TransientError as e:
        if attempt < max_retries - 1:
            delay = initial_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
            time.sleep(delay)
            continue
        raise
```

### Cleanup Pattern (Required for scratch orgs)
```python
# Expected pattern
try:
    org_alias = create_scratch_org()
    # ... operations ...
finally:
    delete_scratch_org(org_alias)  # Always executes
```

### Logging Pattern (Required for operations)
```python
# Expected pattern
logger.info(f"Starting operation for task {task_id}")
logger.debug(f"Input preview: {input[:500]}...")
logger.error(f"Operation failed: {error}", exc_info=True)
```

## Anti-Patterns to Flag

### Silent Failures
```python
# BAD
try:
    operation()
except Exception:
    pass  # Silent failure

# GOOD
try:
    operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

### Resource Leaks
```python
# BAD
org = create_scratch_org()
deploy(org)
# org never deleted if deploy fails

# GOOD
org = create_scratch_org()
try:
    deploy(org)
finally:
    delete_scratch_org(org)
```

### Hardcoded Secrets
```python
# BAD
api_key = "sk-12345abcde"

# GOOD
api_key = os.environ.get("API_KEY")
```

### Missing Type Hints
```python
# BAD
def process(data):
    return result

# GOOD
def process(data: Dict[str, Any]) -> List[Result]:
    return result
```
