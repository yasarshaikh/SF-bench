#!/bin/bash
# Check for dead links in GitHub Pages documentation
# Verifies both local file existence AND actual HTTP status (like a crawler)
# Properly handles Jekyll permalinks and baseurl

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

# Read baseurl from _config.yml
BASEURL=$(grep -E "^baseurl:" docs/_config.yml | sed 's/.*baseurl:[[:space:]]*["'\'']*\([^"'\'']*\)["'\'']*/\/\1/' | sed 's/^\/\//\//' || echo "")
BASEURL="${BASEURL%/}"  # Remove trailing slash

# Read url from _config.yml
SITE_URL=$(grep -E "^url:" docs/_config.yml | sed 's/.*url:[[:space:]]*["'\'']*\([^"'\'']*\)["'\'']*/\1/' | sed 's/\/$//' || echo "https://yasarshaikh.github.io")

BASE_URL="${SITE_URL}${BASEURL}"

echo -e "${BLUE}Site URL: ${SITE_URL}${NC}"
echo -e "${BLUE}Base URL: ${BASE_URL}${NC}"
echo ""

# Function to extract permalink from Jekyll frontmatter
extract_permalink() {
    local file="$1"
    if [ -f "$file" ]; then
        # Extract permalink from frontmatter
        local permalink=$(grep -E "^permalink:" "$file" | head -1 | sed 's/permalink:[[:space:]]*["'\'']*\([^"'\'']*\)["'\'']*/\1/' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        if [ -n "$permalink" ]; then
            echo "$permalink"
        fi
    fi
}

# Function to resolve link to actual URL
resolve_link_url() {
    local link="$1"
    local source_file="$2"
    
    # Handle absolute permalinks (starting with /)
    if [[ $link == /* ]]; then
        echo "${BASE_URL}${link}"
        return
    fi
    
    # Handle relative paths
    local file_dir=$(dirname "$source_file")
    local rel_dir="${file_dir#docs/}"
    
    # Convert .md to .html for GitHub Pages
    if [[ $link == *.md ]]; then
        link="${link%.md}.html"
    fi
    
    # Build URL
    if [ -n "$rel_dir" ] && [ "$rel_dir" != "." ]; then
        echo "${BASE_URL}/${rel_dir}/${link}"
    else
        echo "${BASE_URL}/${link}"
    fi
}

# Function to check if a file has a permalink
get_file_permalink() {
    local file="$1"
    local permalink=$(extract_permalink "$file")
    if [ -n "$permalink" ]; then
        echo "${BASE_URL}${permalink}"
    else
        # Default: file path relative to docs/
        local rel_path="${file#docs/}"
        rel_path="${rel_path%.md}.html"
        echo "${BASE_URL}/${rel_path}"
    fi
}

# Find all markdown files in docs/
MD_FILES=$(find docs -name "*.md" -type f)

echo -e "${BLUE}Checking internal links (HTTP status verification)...${NC}"
echo ""

for file in $MD_FILES; do
    echo -e "${BLUE}Checking: $file${NC}"
    
    # Extract links (markdown format: [text](url))
    LINKS=$(grep -oE '\[([^\]]+)\]\(([^)]+)\)' "$file" | sed 's/.*(\(.*\))/\1/' || true)
    
    for link in $LINKS; do
        # Skip external links (check separately)
        if [[ $link == http* ]]; then
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 -L "$link" 2>/dev/null || echo "000")
            if [ "$HTTP_CODE" = "200" ]; then
                echo -e "${GREEN}  ✅ External: $link (HTTP 200)${NC}"
            elif [ "$HTTP_CODE" != "000" ]; then
                echo -e "${RED}  ❌ Broken external link: $link (HTTP $HTTP_CODE)${NC}"
                ERRORS=$((ERRORS + 1))
            fi
            continue
        fi
        
        # Skip anchor links
        if [[ $link == \#* ]]; then
            continue
        fi
        
        # Resolve link to full URL
        FULL_URL=$(resolve_link_url "$link" "$file")
        
        # Normalize URL
        FULL_URL=$(echo "$FULL_URL" | sed 's|/\./|/|g' | sed 's|//|/|g' | sed 's|:/|://|')
        
        # Check HTTP status (PRIMARY CHECK - like a crawler)
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 -L "$FULL_URL" 2>/dev/null || echo "000")
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}  ✅ $link (HTTP 200)${NC}"
        elif [ "$HTTP_CODE" = "404" ]; then
            echo -e "${RED}  ❌ Broken link: $link (HTTP 404)${NC}"
            echo -e "${RED}      Checked URL: $FULL_URL${NC}"
            ERRORS=$((ERRORS + 1))
        elif [ "$HTTP_CODE" = "000" ]; then
            # Network error - check local file as fallback
            local target_file=""
            if [[ $link == /* ]]; then
                # Absolute path - try to find file with this permalink
                local search_path="${link#/}"
                target_file=$(find docs -name "*.md" -exec grep -l "permalink:.*${search_path}" {} \; | head -1)
            else
                # Relative path
                local file_dir=$(dirname "$file")
                if [[ $link == *.md ]]; then
                    target_file="$file_dir/${link}"
                else
                    target_file="$file_dir/${link%.html}.md"
                fi
            fi
            
            if [ -f "$target_file" ]; then
                echo -e "${YELLOW}  ⚠️  $link (local file exists, HTTP check failed - network issue?)${NC}"
                WARNINGS=$((WARNINGS + 1))
            else
                echo -e "${RED}  ❌ Broken link: $link (HTTP check failed, file not found)${NC}"
                echo -e "${RED}      Checked URL: $FULL_URL${NC}"
                ERRORS=$((ERRORS + 1))
            fi
        else
            echo -e "${RED}  ❌ Broken link: $link (HTTP $HTTP_CODE)${NC}"
            echo -e "${RED}      Checked URL: $FULL_URL${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    done
done

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
