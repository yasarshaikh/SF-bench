#!/bin/bash
# Post-work verification script for SF-Bench
# Run this after making changes to ensure repo is ready for public GitHub

set -e

echo "🔍 SF-Bench Repository Verification"
echo "===================================="
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check 1: No secrets
echo -e "${BLUE}1. Checking for secrets...${NC}"
if grep -r -E "(api[_-]?key|password|secret|token|credential)\s*[:=]\s*['\"][^'\"]{10,}" --include="*.py" --include="*.md" --include="*.json" --include="*.txt" --exclude-dir=_internal --exclude-dir=.git --exclude-dir=__pycache__ . 2>/dev/null | grep -v "API key" | grep -v "api_key" | grep -v "example"; then
    echo -e "${RED}❌ ERROR: Potential secrets found!${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✅ No secrets found${NC}"
fi

# Check 2: Python syntax
echo -e "${BLUE}2. Checking Python syntax...${NC}"
PY_FILES=$(find . -name "*.py" -not -path "./_internal/*" -not -path "./.git/*" -not -path "*/__pycache__/*" -not -path "./venv/*" -not -path "./env/*")
SYNTAX_ERRORS=0
for file in $PY_FILES; do
    if ! python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${RED}  ❌ Syntax error in $file${NC}"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done
if [ $SYNTAX_ERRORS -eq 0 ]; then
    echo -e "${GREEN}  ✅ All Python files compile${NC}"
else
    ERRORS=$((ERRORS + SYNTAX_ERRORS))
fi

# Check 3: No cache files tracked
echo -e "${BLUE}3. Checking for tracked cache files...${NC}"
if git ls-files | grep -E "(__pycache__|\.pyc$|\.pyo$)"; then
    echo -e "${RED}❌ ERROR: Cache files are tracked in git!${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✅ No cache files tracked${NC}"
fi

# Check 4: No log files tracked
echo -e "${BLUE}4. Checking for tracked log files...${NC}"
if git ls-files | grep -E "\.log$"; then
    echo -e "${RED}❌ ERROR: Log files are tracked in git!${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✅ No log files tracked${NC}"
fi

# Check 5: No _internal files tracked
echo -e "${BLUE}5. Checking for tracked _internal files...${NC}"
if git ls-files | grep "^_internal/"; then
    echo -e "${RED}❌ ERROR: _internal/ files are tracked in git!${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✅ No _internal files tracked${NC}"
fi

# Check 6: Required files exist
echo -e "${BLUE}6. Checking required files...${NC}"
REQUIRED_FILES=("README.md" "LICENSE" "CONTRIBUTING.md" "CODE_OF_CONDUCT.md" "Agents.md" ".gitignore")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}  ✅ $file exists${NC}"
    else
        echo -e "${RED}  ❌ $file missing${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check 7: Test imports
echo -e "${BLUE}7. Checking test imports...${NC}"
if python3 -c "import sys; sys.path.insert(0, '.'); from sfbench.utils.checkpoint import CheckpointManager; from sfbench.utils.schema import EvaluationReport; print('✅ Core imports work')" 2>/dev/null; then
    echo -e "${GREEN}  ✅ Core modules import successfully${NC}"
else
    echo -e "${RED}  ❌ Import errors detected${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 8: Documentation links (basic check)
echo -e "${BLUE}8. Checking documentation structure...${NC}"
if [ -f "docs/index.md" ] && [ -f "docs/quickstart.md" ]; then
    echo -e "${GREEN}  ✅ Core documentation files exist${NC}"
else
    echo -e "${YELLOW}  ⚠️  Some documentation files missing${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 9: .gitignore is comprehensive
echo -e "${BLUE}9. Checking .gitignore...${NC}"
if grep -q "_internal/" .gitignore && grep -q "*.log" .gitignore && grep -q "__pycache__" .gitignore; then
    echo -e "${GREEN}  ✅ .gitignore looks comprehensive${NC}"
else
    echo -e "${YELLOW}  ⚠️  .gitignore may be incomplete${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "===================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Repository verification PASSED${NC}"
    echo "   Ready for public GitHub!"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Repository verification PASSED with $WARNINGS warning(s)${NC}"
    exit 0
else
    echo -e "${RED}❌ Repository verification FAILED with $ERRORS error(s)${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}   and $WARNINGS warning(s)${NC}"
    fi
    exit 1
fi
