#!/bin/bash
# Check for dead links in GitHub Pages documentation
# Run this to verify all links work before pushing

set -e

echo "🔗 Checking GitHub Pages Links"
echo "==============================="
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="https://yasarshaikh.github.io/SF-bench"

# Find all markdown files in docs/
MD_FILES=$(find docs -name "*.md" -type f)

echo -e "${BLUE}Checking internal links in documentation...${NC}"
echo ""

for file in $MD_FILES; do
    echo -e "${BLUE}Checking: $file${NC}"
    
    # Extract links (markdown format: [text](url))
    LINKS=$(grep -oE '\[([^\]]+)\]\(([^)]+)\)' "$file" | sed 's/.*(\(.*\))/\1/' || true)
    
    for link in $LINKS; do
        # Skip external links
        if [[ $link == http* ]]; then
            continue
        fi
        
        # Skip anchor links
        if [[ $link == \#* ]]; then
            continue
        fi
        
        # Convert .md to .html for GitHub Pages
        if [[ $link == *.md ]]; then
            link="${link%.md}.html"
        fi
        
        # Resolve relative paths
        if [[ $link == /* ]]; then
            # Absolute path from docs root
            target_file="docs${link}"
        else
            # Relative path
            file_dir=$(dirname "$file")
            target_file="$file_dir/$link"
        fi
        
        # Check if file exists
        if [ ! -f "$target_file" ] && [ ! -d "$target_file" ]; then
            echo -e "${RED}  ❌ Broken link: $link (in $file)${NC}"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${GREEN}  ✅ $link${NC}"
        fi
    done
done

# Check for common broken patterns
echo ""
echo -e "${BLUE}Checking for common issues...${NC}"

# Check for .md links that should be .html
MD_LINKS=$(grep -r "\.md)" docs/ --include="*.md" | grep -v ".md)" | head -5 || true)
if [ -n "$MD_LINKS" ]; then
    echo -e "${YELLOW}  ⚠️  Found .md links (should be .html for GitHub Pages):${NC}"
    echo "$MD_LINKS" | head -5
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "==============================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All links verified!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Links verified with $WARNINGS warning(s)${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $ERRORS broken link(s)${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}   and $WARNINGS warning(s)${NC}"
    fi
    exit 1
fi
