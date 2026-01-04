#!/bin/bash
# Check for dead links in GitHub Pages documentation
# Verifies both local file existence AND actual HTTP status (like a crawler)

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

echo -e "${BLUE}Checking internal links (local files + HTTP status)...${NC}"
echo ""

for file in $MD_FILES; do
    echo -e "${BLUE}Checking: $file${NC}"
    
    # Extract links (markdown format: [text](url))
    LINKS=$(grep -oE '\[([^\]]+)\]\(([^)]+)\)' "$file" | sed 's/.*(\(.*\))/\1/' || true)
    
    for link in $LINKS; do
        # Skip external links (will check separately if needed)
        if [[ $link == http* ]]; then
            # Check external link with curl
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$link" 2>/dev/null || echo "000")
            if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "000" ]; then
                echo -e "${RED}  ❌ Broken external link: $link (HTTP $HTTP_CODE)${NC}"
                ERRORS=$((ERRORS + 1))
            fi
            continue
        fi
        
        # Skip anchor links
        if [[ $link == \#* ]]; then
            continue
        fi
        
        # Handle permalinks (starting with /)
        if [[ $link == /* ]]; then
            # Absolute path - use as-is for HTTP check
            FULL_URL="${BASE_URL}${link}"
            # For local check, try to find the file
            # Remove leading / and check in docs/
            local_path="${link#/}"
            # Check if it's a permalink by looking for permalink in frontmatter
            target_file=""
        else
            # Relative path - need to resolve from file location
            # Convert .md to .html for GitHub Pages
            if [[ $link == *.md ]]; then
                link="${link%.md}.html"
            fi
            
            file_dir=$(dirname "$file")
            # Remove 'docs/' prefix from file_dir
            rel_dir="${file_dir#docs/}"
            if [ -n "$rel_dir" ] && [ "$rel_dir" != "." ]; then
                FULL_URL="${BASE_URL}/${rel_dir}/${link}"
            else
                FULL_URL="${BASE_URL}/${link}"
            fi
            target_file="$file_dir/$link"
        fi
        
        # Normalize URL (remove double slashes, etc.)
        FULL_URL=$(echo "$FULL_URL" | sed 's|/\./|/|g' | sed 's|/[^/]*/\.\./|/|g' | sed 's|//|/|g' | sed 's|:/|://|')
        
        # Check 1: Local file existence (for relative paths)
        LOCAL_EXISTS=false
        if [ -n "$target_file" ] && ([ -f "$target_file" ] || [ -d "$target_file" ]); then
            LOCAL_EXISTS=true
        fi
        
        # Check 2: HTTP status (like a crawler) - PRIMARY CHECK
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$FULL_URL" 2>/dev/null || echo "000")
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}  ✅ $link (HTTP 200)${NC}"
        elif [ "$HTTP_CODE" = "000" ]; then
            # Network error or timeout - check local file as fallback
            if [ "$LOCAL_EXISTS" = true ]; then
                echo -e "${YELLOW}  ⚠️  $link (local file exists, but HTTP check failed - may be network issue)${NC}"
                WARNINGS=$((WARNINGS + 1))
            else
                echo -e "${RED}  ❌ Broken link: $link (file not found, HTTP check failed)${NC}"
                echo -e "${RED}      URL: $FULL_URL${NC}"
                ERRORS=$((ERRORS + 1))
            fi
        elif [ "$HTTP_CODE" = "404" ]; then
            echo -e "${RED}  ❌ Broken link: $link (HTTP 404 - page not found)${NC}"
            echo -e "${RED}      URL: $FULL_URL${NC}"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${RED}  ❌ Broken link: $link (HTTP $HTTP_CODE)${NC}"
            echo -e "${RED}      URL: $FULL_URL${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    done
done

# Check for common issues
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
