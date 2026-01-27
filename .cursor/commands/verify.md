# Verify

Run comprehensive verification of recent work.

## Purpose

Acts as an independent "judge" to verify work quality before considering it complete. Inspired by Boris Cherny's principle: "The most important thing to get great results — give Claude a way to verify its work."

## Verification Checks

### Critical (Block Completion)
1. **No Secrets** — Scans for API keys, tokens, credentials
2. **Professional Language** — No profanity or inappropriate content
3. **Tests Pass** — All existing tests must pass

### Important (Should Fix)
4. **No Debug Artifacts** — No print statements, debugger, TODO without issue
5. **Linting** — No syntax errors or major violations

## Usage

### Automatic (via hooks)
Verification runs automatically on session stop.

### Manual
```bash
# Verify specific files
echo '{"edited_files": ["sfbench/engine.py", "sfbench/config.py"]}' | python .cursor/hooks/verify_work.py

# Verify all Python files changed in git
git diff --name-only | grep ".py$" | xargs -I {} echo '{}' | python -c "
import sys, json
files = [line.strip() for line in sys.stdin if line.strip()]
print(json.dumps({'edited_files': files}))
" | python .cursor/hooks/verify_work.py
```

## Verification Report

```
==================================================
VERIFICATION REPORT: ✅ PASSED / ❌ FAILED
Files checked: N
==================================================

✅ No Secrets
✅ No Debug Artifacts
✅ Professional Language
✅ Linting
✅ Tests
```

## Self-Review Checklist

Before declaring work done:

```
□ Read the diff as a code reviewer
□ Question each change: "Is this necessary?"
□ Verify the change works (run it, test it)
□ Confirm minimal surface area achieved
□ Would I approve this PR?
```

## When Verification Fails

### Critical Failure
1. **STOP** — Do not proceed
2. **FIX** — Address the critical issue
3. **RE-RUN** — Verify again

### Non-Critical Warning
1. **ASSESS** — Is this acceptable?
2. **FIX** — If time permits
3. **DOCUMENT** — Note if skipping

## Philosophy

> "Verification is not optional. Every change must prove it works, not just claim to work."
