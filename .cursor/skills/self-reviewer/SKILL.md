---
name: self-reviewer
description: Performs independent self-review of completed work to catch issues before they become problems. The agent invokes this skill when completing tasks, reviewing changes, or validating quality.
---

# Self-Reviewer

## Overview

This skill implements Boris Cherny's verification principle: "The most important thing to get great results — give Claude a way to verify its work."

The self-reviewer acts as an independent judge, applying critical scrutiny to work before it's considered complete.

## When This Skill Applies

- After completing any code change
- Before declaring a task done
- When reviewing a PR or change
- When quality is uncertain

## The Verification Protocol

### Step 1: Re-Read the Requirement

Before reviewing code, re-read the original request:
- What was actually asked?
- What are the acceptance criteria?
- Are there implicit requirements?

### Step 2: Review the Diff

Read the diff as if you're a senior code reviewer:

```
FOR EACH CHANGE:
  □ Is this change necessary for the task?
  □ Could this be simpler?
  □ Does it follow existing patterns?
  □ Is it the minimal change needed?
```

### Step 3: Check for Common Issues

#### Security Issues
```
□ No hardcoded secrets
□ No PII exposed
□ No internal URLs/IPs
□ Input validation present
```

#### Code Quality Issues
```
□ No debug prints left
□ No commented-out code
□ No TODO without issue link
□ No magic numbers
□ No duplicate code
```

#### Style Issues
```
□ Consistent naming
□ Proper indentation
□ Import order correct
□ Line length within limits
```

### Step 4: Verify It Works

Don't assume — verify:

```
□ Run the code (not just compile)
□ Test the happy path
□ Test an error case
□ Check for regressions
```

### Step 5: Ask Critical Questions

```
1. Would I approve this PR if someone else submitted it?
2. Would I be proud to have my name on this code?
3. Is there anything that could embarrass the team?
4. Is the change smaller than it could be?
```

## Red Flags to Catch

### Over-Engineering
```
SIGNS:
- Abstract classes with single implementation
- Factories for simple instantiation
- Configuration for non-varying values
- Interfaces with one implementer

ACTION: Simplify
```

### Under-Testing
```
SIGNS:
- Happy path only
- No edge cases
- No error scenarios
- "It should work"

ACTION: Add tests
```

### Scope Creep
```
SIGNS:
- Refactoring unrelated code
- "While I'm here" changes
- Formatting changes in unrelated files
- New features not in requirements

ACTION: Revert extras, separate PR
```

### Fragility
```
SIGNS:
- No error handling
- Assumed inputs always valid
- No null checks
- No timeout/retry

ACTION: Add defensive code
```

## The Final Checklist

Before saying "done", complete this checklist:

```
FUNCTIONALITY:
□ Meets the original requirement
□ No regressions introduced
□ Edge cases handled
□ Errors handled gracefully

QUALITY:
□ Code is readable
□ Follows existing patterns
□ Properly documented
□ Tests pass

SAFETY:
□ No secrets exposed
□ No security issues
□ No performance issues
□ No breaking changes

MINIMAL:
□ Every line is necessary
□ No scope creep
□ No over-engineering
□ Smallest possible change
```

## Self-Deception Traps

Watch for these cognitive biases:

### Confirmation Bias
"It works because I expect it to work"
→ **Test with unexpected inputs**

### Sunk Cost Fallacy
"I spent hours on this approach, it must be right"
→ **Willing to start over if needed**

### Optimism Bias
"The edge cases probably don't matter"
→ **Test the edge cases anyway**

### Anchoring
"The first solution I thought of is best"
→ **Consider at least one alternative**

## Output Format

When self-reviewing, document findings:

```markdown
## Self-Review: [Task/PR]

### Requirement Check
- [ ] Meets requirements: YES/NO

### Quality Check
- Passed: X items
- Warnings: Y items
- Failed: Z items

### Issues Found
1. [Issue description] - [Severity] - [Fixed: YES/NO]

### Final Assessment
- [ ] Ready to merge: YES/NO
- [ ] Confidence: HIGH/MEDIUM/LOW

### Notes
[Any observations or concerns]
```

## Integration with Hooks

The self-reviewer integrates with:
- `verify_work.py` hook — Automated checks
- `session_complete.py` hook — Session logging
- Pre-commit hooks — Blocking checks

Run manual review in addition to automated checks.
