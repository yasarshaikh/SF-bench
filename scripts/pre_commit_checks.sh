#!/bin/bash
# Pre-commit checks for SF-Bench
# Can be run manually or as part of git hooks

set -e

echo "🔍 Running pre-commit checks..."
echo ""

ERRORS=0

# Check 1: Python syntax
echo "1. Checking Python syntax..."
STAGED_PY=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
if [ -n "$STAGED_PY" ]; then
    for file in $STAGED_PY; do
        if ! python3 -m py_compile "$file" 2>/dev/null; then
            echo "  ❌ Syntax error in $file"
            ERRORS=$((ERRORS + 1))
        fi
    done
    if [ $ERRORS -eq 0 ]; then
        echo "  ✅ All Python files compile"
    fi
fi

# Check 2: No secrets
echo "2. Checking for secrets..."
if git diff --cached | grep -E "(api[_-]?key|password|secret|token)\s*[:=]\s*['\"][^'\"]{10,}" 2>/dev/null; then
    echo "  ❌ ERROR: Potential secrets detected!"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ No secrets found"
fi

# Check 3: No _internal files
echo "3. Checking for internal files..."
if git diff --cached --name-only | grep "^_internal/"; then
    echo "  ❌ ERROR: _internal/ files should not be committed!"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ No internal files"
fi

# Check 4: No cache/temp files
echo "4. Checking for cache/temp files..."
TEMP_FILES=$(git diff --cached --name-only | grep -E '(\.pyc$|__pycache__|\.log$|\.tmp$|\.bak$)' || true)
if [ -n "$TEMP_FILES" ]; then
    echo "  ❌ ERROR: Temporary files detected:"
    echo "$TEMP_FILES"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ No cache/temp files"
fi

# Summary
echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All pre-commit checks passed!"
    exit 0
else
    echo "❌ Pre-commit checks failed with $ERRORS error(s)"
    exit 1
fi
